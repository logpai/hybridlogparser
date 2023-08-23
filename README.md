# hybridlogparser

### !!!UNDER CONSTRUCTION

## Preliminary

Hybrid log parsing is a **superset** of existing log parsing research that targets single-line logs. It focuses on single-line logs (e.g., typical execution logs), multi-line logs (e.g, exception logs or tabular system status logs), and their mix.

Hybrid log parsers are designed to handle hybrid log parsing task, which is challenging for traditional [log parsers](https://github.com/logpai/logparser) due to the structural variability of hybrid logs.

## Contents

### Datasets

| Dataset | Description | #Event Template | #Table Template | # Text Template | Raw size |
| :-------: | :-----------: | :---: | :---: | :---: | :---: |
| HiBench | The logs of a common benchmark for HPC | 93 | 7 | 43 | 1.6MB |
| CTS | The system logs from a cloud testing service | 92 | 7 | 18 | 61KB |

### Parsers

| Parsers | Paper Title |
| :-------: | ----------- |
| Hue| Junjielong Xu, Qiuai Fu, Zhouruixing Zhu, Yutong Cheng, Zhijing Li, Yuchi Ma, Pinjia He. [Hue: A User-Adaptive Parser for Hybrid Logs](https://arxiv.org/abs/2308.07085). Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE), 2023 |