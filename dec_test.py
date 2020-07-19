from metrics_test import MetricsTest
import matplotlib.pyplot as plt
import os
import numpy as np

# locals
import utils

class DecTest(MetricsTest):

    def __init__(self):
        super().__init__()

    def check_config(self, config):
        super().check_config(config)

    def collect_data(self, config):
        data = super().collect_data(config)
        return data

    def run(self, config, data):
        results = super().run(config, data)
        return results

    def visualize(self, config, data, results):
        super().visualize(config, data, results)
        if config['publish_plots']:
            for metric in results.keys():
                fig, ax = plt.subplots()
                stds_key = metric.replace('_mean', '') + '_std'
                stds = data.get(stds_key, np.zeros_like(data[metric]))
                ax.errorbar(data['label_value'], data[metric], stds, linestyle='None', marker='.')
                x_scale = 'log' if data[utils.LABEL_NAME_FIELD] == 'topk' else 'linear'
                metric_name = metric.replace(utils.METRIC_FIELD_PREFIX, '')
                title_str  = '{} - {} - {}\n pearson-cor [{:.2f}], spearman-cor [{:.2f}]'.format(
                    config['exp_name'], config['sub_exp_name'], metric_name,
                    results[metric]['pearson_cor'], results[metric]['spearman_cor'])
                ax.set(xlabel=data[utils.LABEL_NAME_FIELD], ylabel='Score', xscale=x_scale, title=title_str)
                fig.savefig(os.path.join(config['out_dir'], '{}_{}_{}.png'.format(
                    config['exp_name'], config['sub_exp_name'], metric_name)))
                plt.close()

    def export(self, config, data, results):
        super().export(config, data, results)
