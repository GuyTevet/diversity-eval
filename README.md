# Evaluating the Evaluation of Diversity in Natural Language Generation

arxiv.org/abs/2004.02990

Our code and data are a platform for evaluating NLG diversity *metrics*.

## What's released?
Basically everything!

#### Data
- Data used for our experiments
- McDiv dataset

#### Code
- Running the metrics used in the paper (and easily add your own)
- Running all of our experiments (soon!)

## Get Data
If you are also running the code, the data will be downloaded automatically.
Otherwise, the data can be downloaded manually from [here](http://diversity-eval.s3-us-west-2.amazonaws.com/data.zip).

## Requirements
The code is running on `python3`.
- For running neural metrics, both `tensorflow >= 1.12` and `pytorch >= 1.0.1` are needed.
- For running *BERT-score*, install `pip install bert_score`
- For running *sent-BERT*, install `pip install sentence_transformers`
- Running BERT-sts is less straightforward; you can either mute it by turning `BertSts`'s `use_me = False` in `diversity_metrics.py` or do the followings:
    - clone `github.com/GuyTevet/bert-sts.git` to `../bert-sts`
    - unzip [checkpoints](http://diversity-eval.s3-us-west-2.amazonaws.com/sts_checkpoints.zip) to `../bert-sts/sts_output`

## Run Metrics
For running all metrics over all the data, use:
```sh
python run_metrics.py
```
This will download the data with all the metrics already calculated, and do nothing because they are already calculated ;)
If you wish to specify file or directory and override it with local metrics calculations, you can run for example:
```sh
python run_metrics.py --input_csv ./data/raw/McDiv_nuggets --override
```
If you wish to specify metrics to run, you can also add them by their class name (comma separated) like this:
```sh
python run_metrics.py --metrics BertSts,AveragedCosineSimilarity
```

#### How to add your own metrics?
Your new metric must be impemented in `diversity_metrics.py` and include the static variables:
```python
use_me = True
default_config = {} # your config comes here
```

**If you wish to implement a plain diversity metric** (that is not derived from a similarity metric), just inherit `metric.DiversityMetric` and implement the `__init__` and `__call__` methods. You can take `DistinctNgrams` as a code example.

**If you wish to implement a diversity metric that derived from a similarity metric**, first implement your similarity metric in `similarity_metrics.py` inherit `metric.SimilarityMetric`, take for example `CosineSimilarity`.
Then, in `diversity_metrics.py`, implement the derived diversity metric, inherit `metric.Similarity2DiversityMetric`, and specify your similarity metric at the `__call__` method, like in `CosineSimilarity2Diversity`.

Note that for neural metrics, we use the more complex `metric.Similarity2DiversityFromFileMetric` base class, which also includes caching.

## Run Experiments
TBD soon

#### How to add your own experiment?
TBD soon

#### How to implement your own diversity test?
TBD soon