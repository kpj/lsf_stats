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


def main(fname, max_job_count, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # read data
    df = pd.read_csv(fname, parse_dates=['date'])
    df.dropna(inplace=True)

    # df = df[~df['note'].str.contains('exit code 143')]

    # convert MB to Bytes
    df['avg_memory'] *= 1_000_000
    df['max_memory'] *= 1_000_000

    # improve readbility
    df['avg_memory_nat'] = df['avg_memory'].apply(humanize.naturalsize)
    df['max_memory_nat'] = df['max_memory'].apply(humanize.naturalsize)

    df['duration_nat'] = df['duration'].apply(humanize.naturaldelta)

    # quick overview
    pyskim.skim(df)

    # histograms
    fig, ax_list = plt.subplots(ncols=2, figsize=(8 * 2, 6), constrained_layout=True)

    ax = ax_list[0]
    sns.histplot(data=df, x='duration', hue='note', log_scale=True, ax=ax)
    ax.xaxis.set_major_formatter(duration_fmt)
    ax.set_xlabel('Job Runtime')

    ax = ax_list[1]
    sns.histplot(data=df, x='avg_memory', hue='note', log_scale=True, ax=ax)
    ax.xaxis.set_major_formatter(size_fmt)
    ax.set_xlabel('Job Average Memory Requirements')

    # ax = ax_list[2]
    # sns.histplot(data=df, x='max_memory', hue='note', log_scale=True, ax=ax)
    # ax.xaxis.set_major_formatter(size_fmt)

    fig.savefig(outdir / 'overview.pdf')

    # memory vs duration scatterplot
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

    sns.scatterplot(data=df, x='duration', y='avg_memory', hue='note')

    ax.xaxis.set_major_formatter(duration_fmt)
    ax.yaxis.set_major_formatter(size_fmt)

    fig.savefig(outdir / 'scatterplot.pdf')

    # successful job counts
    fig, ax = plt.subplots(figsize=(8, 6))

    df[df['successful']].drop_duplicates(subset=['wildcards']).assign(
        date_hour=df['date'].dt.round('H')
    ).groupby('date_hour').size().cumsum().plot(
        xlabel='Date', ylabel='Number of successful jobs', ax=ax
    )

    if max_job_count is not None:
        ax.axhline(int(max_job_count), color='red', ls='dashed')

    fig.tight_layout()
    fig.savefig(outdir / 'job_completions.pdf')
