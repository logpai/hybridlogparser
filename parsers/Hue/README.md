# README

## Environment

- Python 3.9
- Libs:
  - yaml
  - hashlib
  - numpy
  - matplotlib
  - pandas
  - tqdm

Run:

```python
pip install xxx # xxx is the name of libs
```

for setting up the environments.

## Reproduction

To reproduce the experiment, you first need to go to the "artifact" path.

```shell
cd parsers/Hue
```

### 1. Auto Hybrid Log Parsing

Run the program entry of each parser `benchmark/<PARSER>_benchmark.py` to re-produce the parsed log files and evaluate the parsing performance.

```shell
python demo.py
```

The parsing results are as follows:

```      
Dataset: HiBench        Accuracy: 0.9320        Recall: 0.8584  Precision: 0.8151       F1-Score: 0.8362
Dataset: CTS    Accuracy: 0.8482        Recall: 0.8865  Precision: 0.7962       F1-Score: 0.8389
```

### 2. Guided Hybrid Log Parsing

Before starting, you need to change some settings first:

1. Open "Hue.py":

   ```
   vim Hue.py
   ```
2. Adjust the `feedback` flag from "False" to "True".

   From:

   ```python
   feedback = False # whether to enable feedback query
   ```

   To:

   ```python
   feedback = True # whether to enable feedback query
   ```
3. Change the `feedback_target` object to the dataset you want to reproduce

   ```python
   feedback_target = 'Linux' # choose a dataset for feedback experiment
   ```
4. Re-run the benchmark script:

   ```python
   python demo.py
   ```

You can then interact with the command line to guide the parser through feedback.

Specifically, each time you enter "Enter" or "y", you will accept the merge, while entering 'n' means you reject the merge.

### 3. Single-line Log Parsing

If you want to parse the single-line logs, please import the logs of [loghub](https://github.com/logpai/loghub) into the `datasets` directory and set the `traditional_logs` variable in the `demo.py` as well:

```python
traditional_logs = ['HDFS', 'Spark', 'BGL', 'Windows', 'Linux', 'Andriod', 'Mac', 'Hadoop', 'HealthApp', 'OpenSSH', 'Thunderbird', 'Proxifier', 'Apache', 'HPC', 'Zookeeper', 'OpenStack']
```
