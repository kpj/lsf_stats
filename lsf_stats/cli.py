import click

from .gather import main as gather_func
from .summarize import main as summarize_func


@click.group(help='Summarize LSF job properties by parsing log files.')
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
    '-o',
    '--output',
    default='plots/',
    help='Directory to save plots to.',
)
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
def summarize(filename, max_job_count, output):
    summarize_func(filename, max_job_count, output)
