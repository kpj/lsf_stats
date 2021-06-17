from pathlib import Path

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import pyskim
import humanize


@FuncFormatter
def size_fmt(x, pos):
    return humanize.naturalsize(x)


@FuncFormatter
def duration_fmt(x, pos):
    return humanize.naturaldelta(x)


def extract_wildcards(ser):
    assert ser.shape[0] == 1
    wc_str = ser.iloc[0]

    for entry in wc_str.split(', '):
        key, value = entry.split('=', 1)
        ser[key] = value

    return ser


def main(fname, max_job_count, split_wildcards, grouping_variable, query, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # read data
    df = pd.read_csv(fname, parse_dates=['date'])
    df.dropna(inplace=True)

    if query is not None:
        df = df.query(query).copy()

    # convert MB to Bytes
    df['avg_memory'] *= 1_000_000
    df['max_memory'] *= 1_000_000

    # improve readbility
    df['avg_memory_nat'] = df['avg_memory'].apply(humanize.naturalsize)
    df['max_memory_nat'] = df['max_memory'].apply(humanize.naturalsize)

    df['duration_nat'] = df['duration'].apply(humanize.naturaldelta)

    # split wildcards
    if split_wildcards:
        df_wildcards = df['wildcards'].to_frame().apply(extract_wildcards, axis=1)
        df = df.drop('wildcards', axis=1).merge(
            df_wildcards,
            left_index=True,
            right_index=True,
            suffixes=(None, '_wildcard'),
        )

    # quick overview
    pyskim.skim(df)

    # histograms
    fig, ax_list = plt.subplots(ncols=2, figsize=(8 * 2, 6), constrained_layout=True)

    ax = ax_list[0]
    sns.histplot(data=df, x='duration', hue=grouping_variable, log_scale=True, ax=ax)
    ax.xaxis.set_major_formatter(duration_fmt)
    ax.set_xlabel('Job Runtime')

    ax = ax_list[1]
    sns.histplot(data=df, x='avg_memory', hue=grouping_variable, log_scale=True, ax=ax)
    ax.xaxis.set_major_formatter(size_fmt)
    ax.set_xlabel('Job Average Memory Requirements')

    # ax = ax_list[2]
    # sns.histplot(data=df, x='max_memory', hue=grouping_variable, log_scale=True, ax=ax)
    # ax.xaxis.set_major_formatter(size_fmt)

    fig.savefig(outdir / 'overview.pdf')

    # memory vs duration scatterplot
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

    sns.scatterplot(data=df, x='duration', y='avg_memory', hue=grouping_variable)

    ax.xaxis.set_major_formatter(duration_fmt)
    ax.yaxis.set_major_formatter(size_fmt)

    fig.savefig(outdir / 'scatterplot.pdf')

    # successful job counts
    tmp = (
        df[df['successful']]
        .sort_values('date')
        .drop_duplicates(subset=['wildcards'])
        .assign(date_hour=df['date'].dt.round('H'))
    )

    if grouping_variable is None:
        tmp_grp = tmp.groupby('date_hour').size()
    else:
        tmp_grp = (
            tmp.groupby([grouping_variable, 'date_hour'])
            .size()
            .reset_index()
            .pivot(columns=[grouping_variable], index=['date_hour'])
            .fillna(0)
        )

        tmp_grp.columns = tmp_grp.columns.droplevel(0)

    df_jobcounts = tmp_grp.cumsum()

    fig, ax = plt.subplots(figsize=(8, 6))

    df_jobcounts.plot(xlabel='Date', ylabel='Number of successful jobs', ax=ax)

    if max_job_count is not None:
        ax.axhline(int(max_job_count), color='red', ls='dashed')

    fig.tight_layout()
    fig.savefig(outdir / 'job_completions.pdf')
