import os
import shutil
import subprocess
import csv
import bert_score
import sentence_transformers
import numpy as np
from scipy.spatial.distance import cosine

# locals
import metric
import similarity_metrics
import utils

class DistinctNgrams(metric.DiversityMetric):

    default_config = {'n': 3}

    def __init__(self, config):
        super().__init__(config)

        # validate config
        self.uint_assert('n')

    def normalized_unique_ngrams(self, ngram_lists):
        """
        Calc the portion of unique n-grams out of all n-grams.
        :param ngram_lists: list of lists of ngrams
        :return: value in (0,1]
        """
        ngrams = [item for sublist in ngram_lists for item in sublist]  # flatten
        return len(set(ngrams)) / len(ngrams) if len(ngrams) > 0 else 0.

    def __call__(self, response_set):
        super().__call__(response_set)
        return self.normalized_unique_ngrams(utils.lines_to_ngrams(response_set, n=self.config['n']))


class AveragedDistinctNgrams(metric.AveragedNgramDiversityMetric):

    use_me = True
    default_config = {'n_min': 1, 'n_max': 5}

    def __init__(self, config):
        super().__init__(config, DistinctNgrams)


class CosineSimilarity2Diversity(metric.Similarity2DiversityMetric):

    default_config = {'n': 3}

    def __init__(self, config):
        super().__init__(config, similarity_metrics.CosineSimilarity)


class AveragedCosineSimilarity(metric.AveragedNgramDiversityMetric):

    use_me = True
    default_config = {'n_min': 1, 'n_max': 5}

    def __init__(self, config):
        super().__init__(config, CosineSimilarity2Diversity)


class BertScore(metric.Similarity2DiversityFromFileMetric):

    use_me = True

    def __init__(self, config):
        super().__init__(config)

    def calc_scores(self):
        super().calc_scores()

        # write input_tsv
        self.create_input_tsv()

        # read data
        with open(self.config['input_tsv'], 'r+', encoding='utf-8') as f_in:
            cands = []
            refs = []
            reader = csv.DictReader(f_in, dialect='excel-tab')  # tsv reader
            for row in reader:
                refs.append(row['sentence1'])
                cands.append(row['sentence2'])

        # calc scores
        P, R, F = bert_score.score(cands, refs, idf=False, lang='en', rescale_with_baseline=True)

        # write scores
        output_str = '\n'.join(['{:.5f}'.format(e) for e in F.tolist()]) + '\n'
        with open(self.config['cache_file'], 'w', encoding='utf-8') as f_out:
            f_out.write(output_str)


class BertSts(metric.Similarity2DiversityFromFileMetric):

    use_me = True

    def __init__(self, config):
        super().__init__(config)

    def calc_scores(self):
        super().calc_scores()

        # write input_tsv
        self.create_input_tsv()

        sts_dir_path = '../bert-sts' # FIXME - hard coded
        if not os.path.isdir(sts_dir_path):
            raise OSError('[{}] not found'.format(sts_dir_path))

        # inits
        run_dir = 'tmp_run'
        abs_input_tsv = os.path.abspath(self.config['input_tsv'])
        abs_output_tsv = os.path.abspath(self.config['cache_file'])

        # move to sts dir
        cur_dir = os.getcwd()
        os.chdir(sts_dir_path)

        # create the test dir
        if os.path.isdir(run_dir):
            shutil.rmtree(run_dir)
        os.mkdir('tmp_run')
        shutil.copy(abs_input_tsv, os.path.join(run_dir, 'test.tsv'))

        # run bert-sts
        subprocess.run(['bash', 'infer_sts.sh', '-i', run_dir, '-o', run_dir])

        # copy back results
        shutil.copy(os.path.join(run_dir, 'test_results.tsv'), abs_output_tsv)

        # return to current dir
        shutil.rmtree(run_dir)
        os.chdir(cur_dir)

class SentBert(metric.Similarity2DiversityFromFileMetric):

    use_me = True

    def __init__(self, config):
        super().__init__(config)
        self.similarity_metric = lambda vector_a, vector_b: 1 - cosine(vector_a, vector_b)

    def calc_scores(self):
        super().calc_scores()

        # write input_tsv
        model_name = 'bert-large-nli-stsb-mean-tokens' # FIXME - hard coded
        model = sentence_transformers.SentenceTransformer(model_name)
        resp_list = []

        # read resps
        with open(self.config['input_path'], 'r+', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            resp_keys = sorted([s for s in reader.fieldnames if
                                s.startswith('resp_') and utils.represents_int(s.split('resp_')[-1])])
            for row in reader:
                resps = [v for k, v in row.items() if k in resp_keys]
                resp_list += resps

        # calc embeds
        embeds = np.array(model.encode(resp_list)) # [ num_contexts * samples_per_context, embed_dim]
        assert len(embeds.shape) == 2
        assert embeds.shape[0] == self.config['num_sets'] * self.config['samples_per_set']
        embeds = np.reshape(embeds, [self.config['num_sets'], self.config['samples_per_set'], -1])

        # write a cache file compatible with the ordering in bert_score and bert_sts
        similarity_scores_list = [] # note: len() assertion are done in get_similarity_scores method
        for set_i in range(self.config['num_sets']):
            for sample_i in range(self.config['samples_per_set']):
                for sample_j in range(sample_i):
                    similarity_scores_list.append(self.similarity_metric(
                        embeds[set_i, sample_i, :], embeds[set_i, sample_j, :]))
        with open(self.config['cache_file'], 'w') as cache_f:
            for score in similarity_scores_list:
                cache_f.write('{:0.3f}\n'.format(score))

        # # write results
        # np.save(self.config['cache_file'], embeds)


if __name__ == '__main__':

    def print_metric(metric, resp_set):
        print('{0}: {1:0.3f}'.format(type(metric).__name__, metric(resp_set)))

    # TEST
    resp_set = ['i am going', 'i am going', 'lets go i i']
    config = {'n': 3}
    print_metric(CosineSimilarity2Diversity(config), resp_set)
    print_metric(DistinctNgrams(config), resp_set)

    avg_config = {'n_min': 1, 'n_max': 5}
    print_metric(AveragedCosineSimilarity(avg_config), resp_set)
    print_metric(AveragedDistinctNgrams(avg_config), resp_set)
