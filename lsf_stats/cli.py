import click

from .gather import main as gather_func
from .summarize import main as summarize_func


@click.group(help='Summarize LSF job properties by parsing log files.')
@click.version_option()
def cli():
    pass


@cli.command(help='Aggregate information from log files in single dataframe.')
@click.option(
    '-o',
    '--output',
    default='log_statistics.csv',
    help='File to store aggregated information in.',
)
@click.argument('directory', type=click.Path(exists=True))
def gather(directory, output):
    gather_func(directory, output)


@cli.command(help='Summarize and visualize aggregated information.')
@click.option(
    '--max-job-count',
    default=None,
    help='Indicate this maximum job count in plots.',
)
@click.option(
    '--split-wildcards',
    is_flag=True,
    help='Split wildcards into individual dataframe columns.',
)
@click.option(
    '--grouping-variable',
    multiple=True,
    help='Stratify plots by this column (can be used multiple times).',
)
@click.option(
    '-q',
    '--query',
    default=None,
    help='Query to subset dataframe before summarizing.',
)
@click.option(
    '-o',
    '--output',
    default='plots/',
    help='Directory to save plots to.',
)
@click.option(
    '--interactive',
    is_flag=True,
    help='Drop into interactive shell after creating summaries.',
)
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
def summarize(
    filename,
    max_job_count,
    split_wildcards,
    grouping_variable,
    query,
    output,
    interactive,
):
    summarize_func(
        filename,
        max_job_count,
        split_wildcards,
        grouping_variable,
        query,
        output,
        interactive,
    )
