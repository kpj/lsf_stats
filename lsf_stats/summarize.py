from pathlib import Path

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import pyskim
import IPython
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


def main(
    fname, max_job_count, split_wildcards, grouping_variable, query, outdir, interactive
):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # read data
    df = pd.read_csv(fname, parse_dates=['date'])
    df.dropna(inplace=True)

    # convert MB to Bytes
    df['avg_memory'] *= 1_000_000
    df['max_memory'] *= 1_000_000

    # improve readability
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

    # apply query
    if query is not None:
        df = df.query(query).copy()

    # handle grouping variable
    if len(grouping_variable) > 0:
        idx_list = df[list(grouping_variable)].dropna().index
        df = df.loc[idx_list].copy()

        groups = df[list(grouping_variable)].apply(lambda x: '\n'.join(x), axis=1)

        grouping_variable = ', '.join(grouping_variable)
        df[grouping_variable] = groups
    else:
        grouping_variable = None

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
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.scatterplot(
        data=df,
        x='duration',
        y='avg_memory',
        hue=grouping_variable,
        ax=ax,
        rasterized=df.shape[0] > 15_000,
    )

    if grouping_variable is not None:
        ax.legend(title=grouping_variable, bbox_to_anchor=(1.05, 1), loc='upper left')

    ax.set_xlabel('Run time')
    ax.set_ylabel('Average Memory')

    ax.xaxis.set_major_formatter(duration_fmt)
    ax.yaxis.set_major_formatter(size_fmt)

    fig.savefig(outdir / 'scatterplot.pdf', bbox_inches='tight', pad_inches=0)

    # plot job counts
    df['date_job_finished'] = df['date'] + df['duration'].apply(
        lambda x: pd.Timedelta(seconds=x)
    )

    tmp = df.sort_values('date_job_finished').assign(
        date_group=lambda x: x['date_job_finished'].dt.round('S')
    )

    if grouping_variable is None:
        tmp_grp = tmp.groupby('date_group').size()
    else:
        tmp_grp = (
            tmp.groupby([grouping_variable, 'date_group'])
            .size()
            .reset_index()
            .pivot(columns=[grouping_variable], index=['date_group'])
            .fillna(0)
        )

        tmp_grp.columns = tmp_grp.columns.droplevel(0)

    tmp_grp.loc[tmp_grp.index.min() - pd.Timedelta(seconds=1)] = 0
    tmp_grp.sort_index(inplace=True)

    df_jobcounts = tmp_grp.cumsum()

    fig, ax = plt.subplots(figsize=(8, 6))

    df_jobcounts.plot(xlabel='Date', ylabel='Number of executed jobs', ax=ax)

    if grouping_variable is not None:
        ax.legend(title=grouping_variable, bbox_to_anchor=(1.05, 1), loc='upper left')

    if max_job_count is not None:
        ax.axhline(int(max_job_count), color='red', ls='dashed')

    fig.savefig(outdir / 'job_completions.pdf', bbox_inches='tight', pad_inches=0)

    # enter interactive shell if requested
    if interactive:
        IPython.embed()
