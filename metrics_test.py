from abc import ABC, abstractmethod
import os
import csv
import json
from scipy.stats import pearsonr, spearmanr, kendalltau, gaussian_kde

# locals
import utils


class MetricsTest(ABC):

    def __init__(self):
        super().__init__()

    def __call__(self, config):
        self.check_config(config)
        data = self.collect_data(config)
        results = self.run(config, data)
        self.visualize(config, data, results)
        self.export(config, data, results)

    @abstractmethod
    def check_config(self, config):
        expected_keys = ['sub_exp_name', 'exp_name', 'input_csv', 'out_dir',
                         'global_results_json', 'publish_plots', 'publish_results', 'class_name']
        for key in expected_keys: assert key in config.keys()
        assert os.path.isfile(config['input_csv'])
        assert os.path.isdir(config['out_dir'])
        assert type(config['publish_plots']) == type(config['publish_results']) == bool
        assert self.__class__.__name__ == config['class_name']

    @abstractmethod
    def collect_data(self, config):
        with open(config['input_csv'], 'r+', encoding='utf-8') as in_csv_f:
            reader = csv.DictReader(in_csv_f)
            fields_to_read = [f for f in reader.fieldnames
                              if f.startswith(utils.LABEL_PREFIX) or f.startswith(utils.METRIC_FIELD_PREFIX)]
            data = {f: [] for f in fields_to_read}
            for row in reader:
                for field in fields_to_read:
                    element = row[field] if field == utils.LABEL_NAME_FIELD else float(row[field])
                    data[field].append(element)
        assert all([e == data[utils.LABEL_NAME_FIELD][0] for e in data[utils.LABEL_NAME_FIELD]])
        data[utils.LABEL_NAME_FIELD] = data[utils.LABEL_NAME_FIELD][0]
        return data

    @abstractmethod
    def run(self, config, data):
        labels_vector = data[utils.LABEL_VAL_FIELD]
        metric_fields = [f for f in data.keys() if f.startswith(utils.METRIC_FIELD_PREFIX) and not f.endswith('_std')]
        results = {f: {} for f in metric_fields}
        for metric_name, metric_results in results.items():
            metric_results['spearman_cor'], _ = spearmanr(labels_vector, data[metric_name])
            metric_results['pearson_cor'], _ = pearsonr(labels_vector, data[metric_name])
        return results

    @abstractmethod
    def visualize(self, config, data, results):
        pass

    @abstractmethod
    def export(self, config, data, results):
        if config['publish_results']:
            # read json if exists
            global_json = {}
            if os.path.isfile(config['global_results_json']):
                with open(config['global_results_json'], 'r+', encoding='utf-8') as json_f:
                    global_json = json.load(json_f)

            # update json
            global_json[config['sub_exp_name']] = results
            with open(config['global_results_json'], 'w') as json_f:
                json.dump(global_json, json_f, indent=4)

            # write results CSVs
            test_score_types = results[list(results.keys())[0]].keys()
            sub_exp_list = list(global_json.keys())
            csv_fields = [''] + sub_exp_list
            for score_type in test_score_types:
                csv_name = '{}_{}.csv'.format(config['exp_name'], score_type)
                csv_dir = os.path.dirname(config['global_results_json'])
                csv_path = os.path.join(csv_dir, csv_name)
                with open(csv_path, 'w') as csv_f:
                    writer = csv.DictWriter(csv_f, fieldnames=csv_fields)
                    writer.writeheader()
                    for metric in results.keys():
                        out_row = {'': metric.replace(utils.METRIC_FIELD_PREFIX, '')}
                        out_row.update({sub: '{:0.2f}'.format(global_json[sub][metric][score_type]) for sub in sub_exp_list})
                        writer.writerow(out_row)
