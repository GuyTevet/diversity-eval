import os
import requests
import re
from tqdm import tqdm
import zipfile

# consts
DATA_DIR = 'data'
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
METRICS_DATA_DIR = os.path.join(DATA_DIR, 'with_metrics')
RESULTS_DIR = 'results'
EXPERIMENTS_DIR = 'experiments'


def dict_print(d, indent=0):
    # code from https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            dict_print(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))


def parse_path_list(path_str, default_path, file_extension='.csv'):
    csv_list = []
    input_split = [default_path] if path_str == '' else path_str.split(',')

    for path in input_split:
        if os.path.isfile(path) and path.endswith(file_extension):
            csv_list.append(path)
        elif os.path.isdir(path):
            for subdir, dirs, files in os.walk(path):
                for file in files:
                    sub_path = os.path.join(subdir, file)
                    if os.path.isfile(sub_path) and sub_path.endswith(file_extension):
                        csv_list.append(sub_path)
        else:
            raise FileNotFoundError('[{}] not exists.'.format(path))

    return csv_list


def CamleCase2snake_case(string):
    # code from https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


def represents_int(s):
    # code from https://stackoverflow.com/questions/1265665/
    # how-can-i-check-if-a-string-represents-an-int-without-using-try-except
    try:
        int(s)
        return True
    except ValueError:
        return False


def lines_to_ngrams(lines, n=3):
    ngrams = []
    for s in lines:
        words = [e for e in s.replace('.','').replace('\n','').split(' ') if e != '']
        ngrams.append([tuple(words[i:i + n]) for i in range(len(words) - n + 1)])
    return ngrams


def stringify_keys(d):
    """Convert a dict's keys to strings if they are not."""
    # code from https://stackoverflow.com/questions/12734517/json-dumping-a-dict-throws-typeerror-keys-must-be-a-string
    for key in d.keys():

        # check inner dict
        if isinstance(d[key], dict):
            value = stringify_keys(d[key])
        else:
            value = d[key]

        # convert nonstring to string if needed
        if not isinstance(key, str):
            # delete old key
            del d[key]
            try:
                d[str(key)] = value
            except Exception:
                try:
                    d[repr(key)] = value
                except Exception:
                    raise

    return d


def download_and_place_data():

    if not os.path.exists(DATA_DIR):

        url = 'http://diversity-eval.s3-us-west-2.amazonaws.com/data.zip'
        target_zip = 'data.zip'
        response = requests.get(url, stream=True)

        # download
        print('Downloading data from [{}]...'.format(url))
        with open(target_zip, "wb") as handle:
            for data in tqdm(response.iter_content(), unit='B', unit_scale=True, unit_divisor=1024):
                handle.write(data)

        # place
        with zipfile.ZipFile(target_zip, 'r') as zip_ref:
            zip_ref.extractall('.')
        os.remove(target_zip)


if __name__ == '__main__':
    pass


