# lsf_stats

[![PyPI](https://img.shields.io/pypi/v/lsf_stats.svg?style=flat)](https://pypi.python.org/pypi/lsf_stats)
[![Tests](https://github.com/kpj/lsf_stats/workflows/Tests/badge.svg)](https://github.com/kpj/lsf_stats/actions)

Summarize LSF job properties by parsing log files.


## Installation

```python
$ pip install lsf_stats
```


## Usage

```bash
$ lsf_stats --help
Usage: lsf_stats [OPTIONS] COMMAND [ARGS]...

  Summarize LSF job properties by parsing log files.

Options:
  --help  Show this message and exit.

Commands:
  gather     Aggregate information from log files in single dataframe.
  summarize  Summarize and visualize aggregated information.
```
