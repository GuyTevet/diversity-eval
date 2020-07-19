import argparse
import json
import os

# locals
import utils
import con_test, dec_test
test_classes = [con_test.ConTest, dec_test.DecTest]


def run_experiment(params):
    # parse experiments
    experiments_dict = {os.path.basename(path).replace('.json', ''): {'experiment_path': path,
                                                                      'config_dict': {}} for path in
                        utils.parse_path_list(params.input_json,
                                              default_path=utils.EXPERIMENTS_DIR,
                                              file_extension='.json')}
    for exp_name, exp_params in experiments_dict.items():
        exp_params.update({'out_dir': os.path.join(utils.RESULTS_DIR, exp_name)})
        # parse each experiment json to config dictionaries
        with open(exp_params['experiment_path'], 'r+', encoding='utf-8') as exp_f:
            exp_json = json.load(exp_f)
            for sub_exp_name, sub_exp_path in exp_json['experiments'].items():
                sub_exp_config = {
                    'exp_name': exp_name,
                    'sub_exp_name': sub_exp_name,
                    'input_csv': sub_exp_path,
                    'out_dir': os.path.join(exp_params['out_dir'], sub_exp_name),
                    'global_results_json': os.path.join(exp_params['out_dir'], 'results.json'),
                    'class_name': exp_json['global_config']['class_name'],
                    'publish_plots': True,
                    'publish_results': True,
                }
                exp_params['config_dict'].update({sub_exp_name: sub_exp_config})

    # instance all tests
    test_dict = {cls.__name__: cls() for cls in test_classes}

    # run experiments
    for exp_name, exp_params in experiments_dict.items():
        print('Running [{}]'.format(exp_name))
        for sub_exp_name, sub_exp_config in exp_params['config_dict'].items():
            print('\t- [{}]'.format(sub_exp_name))
            if not os.path.isdir(sub_exp_config['out_dir']):
                os.makedirs(sub_exp_config['out_dir'])
            test_dict[sub_exp_config['class_name']](sub_exp_config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute experiments according to input json files,'
                                                 ' visualize and summarize results.')

    # main parameters
    parser.add_argument("--input_json", type=str, default='',
                        help='Input results csv file. Support multiple, comma separated, or dirs. '
                             'By default, will handle all files in ./data/experiments/')

    params = parser.parse_args()
    utils.download_and_place_data()
    run_experiment(params)
