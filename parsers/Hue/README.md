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

## Run

### 1. Auto Hybrid Log Parsing

Run the program entry of each parser `demo/Hue_demo.py`

```shell
python demo/Hue_demo.py
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
4. Re-run the demo:

   ```python
   python demo/Hue_demo.py
   ```

You can then interact with the command line to guide the parser through feedback.

Specifically, each time you enter "Enter" or "y", you will accept the merge, while entering 'n' means you reject the merge.

---

To **fully reproduce** the experiment results in the paper, please refer to [this repository](https://github.com/Siyuexi/Hue)
