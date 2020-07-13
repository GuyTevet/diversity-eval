from scipy.spatial.distance import cosine
import numpy as np

# local
import metric
import utils

class CosineSimilarity(metric.SimilarityMetric):

    def __init__(self, config):
        super().__init__(config)

        # validate config
        self.uint_assert('n')

    def ngram_cosine_distance(selff, ngram1, ngram2):
        """
        Calc cosine distannce between (ngram1, ngram2) [[derived from (str1, str2)]] in the n-gram space.
        """

        def intersection(lst1, lst2):
            return list(set(lst1) & set(lst2))

        # acceleration step - if no intersection -> dist = 1.
        if len(intersection(ngram1, ngram2)) == 0:
            return 1.
        else:
            n_space = list(set().union(ngram1, ngram2))

            # vectorize
            vectors = []
            for n_gram in [ngram1, ngram2]:
                vectors.append([n_gram.count(e) for e in n_space])

            return cosine(vectors[0], vectors[1])  # uv/|u||v|

    def ngram_cosine_similarity(self, str1, str2, n):
        ngrams = utils.lines_to_ngrams([str1, str2], n)
        return 1 - self.ngram_cosine_distance(ngrams[0], ngrams[1])

    def __call__(self, resp_a, resp_b):
        super().__call__(resp_b, resp_b)
        return self.ngram_cosine_similarity(resp_a, resp_b, n=self.config['n'])
