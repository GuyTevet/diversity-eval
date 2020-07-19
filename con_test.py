from metrics_test import MetricsTest
import matplotlib.pyplot as plt
import os
import numpy as np

# locals
import utils

class ConTest(MetricsTest):

    def __init__(self):
        super().__init__()

    def check_config(self, config):
        super().check_config(config)

    def collect_data(self, config):
        data = super().collect_data(config)
        return data

    def run(self, config, data):
        results = super().run(config, data)

        # add Optimal Classifier Accuracy score
        labels_vector = data[utils.LABEL_VAL_FIELD]
        for metric_name, metric_results in results.items():
            diff_samples = [p for p, l in zip(data[metric_name], labels_vector) if l == 1.]
            same_samples = [p for p, l in zip(data[metric_name], labels_vector) if l == 0.]
            metric_results['oca'], _ = utils.optimal_classification_accuracy(diff_samples, same_samples)

        return results

    def visualize(self, config, data, results):
        super().visualize(config, data, results)
        if config['publish_plots']:
            for metric in results.keys():
                fig, ax = plt.subplots()
                labels_vector = data[utils.LABEL_VAL_FIELD]
                diff_samples = [p for p, l in zip(data[metric], labels_vector) if l == 1.]
                same_samples = [p for p, l in zip(data[metric], labels_vector) if l == 0.]
                all_samples = data[metric]
                metric_name = metric.replace(utils.METRIC_FIELD_PREFIX, '')
                assert len(all_samples) == len(diff_samples) + len(same_samples)
                hist_range = (min(all_samples), max(all_samples))
                hist_diff, _, _ = ax.hist(diff_samples, range=hist_range, alpha=0.5, bins=20,
                                          label='diverse content ({})'.format(len(diff_samples)))
                hist_same, _, _ = ax.hist(same_samples, range=hist_range, alpha=0.5, bins=20,
                                          label='constant content ({})'.format(len(same_samples)))
                # max_bin_val = max(hist_diff + hist_same)
                # ax.scatter(th, max_bin_val/50., color='black', marker='v', alpha=1., s=80) # threshold annotation
                ax.legend()
                ax.set(xlabel='Metric Values', ylabel='Bin Count',
                       title='{} - {} - {}\n Optimal Classifier Accuracy [{:.2f}], s_cor [{:.2f}]'.format(
                           config['exp_name'], config['sub_exp_name'], metric_name,
                           results[metric]['oca'], results[metric]['spearman_cor']))
                fig.savefig(os.path.join(config['out_dir'], '{}_{}_{}.png'.format(
                    config['exp_name'], config['sub_exp_name'], metric_name)))
                plt.close()

    def export(self, config, data, results):
        super().export(config, data, results)
