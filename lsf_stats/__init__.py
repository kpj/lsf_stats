from .cli import cli

# set version dunder variable
from importlib import metadata

__version__ = metadata.version('lsf_stats')

__all__ = ['__version__', 'main']
