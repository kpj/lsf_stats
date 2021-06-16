import re
from pathlib import Path

import pandas as pd

from tqdm import tqdm


def walk(path):
    for path in Path(path).iterdir():
        if path.is_dir():
            yield from walk(path)
            continue
        yield path.resolve()


def parse_cluster_info(entry):
    # read data
    txt = entry.read_text()

    # gather stats
    date = re.search(f'Started at (?P<date>.+)', txt).group('date')

    successful = 'Successfully completed.' in txt

    try:
        note = re.search(
            re.compile(
                r'-+.*-+\n\n(?P<note>.+)\n\nResource usage summary:',
                re.MULTILINE | re.DOTALL,
            ),
            txt,
        ).group('note')
    except AttributeError:
        note = pd.NA

    try:
        duration = float(
            re.search(r'Run time : +(?P<duration>[\d.]+) sec.', txt).group('duration')
        )
        avg_memory = float(
            re.search(r'Average Memory : +(?P<avg_memory>[\d.]+) MB', txt).group(
                'avg_memory'
            )
        )
        max_memory = float(
            re.search(r'Max Memory : +(?P<max_memory>[\d.]+) MB', txt).group(
                'max_memory'
            )
        )
    except AttributeError:
        duration = pd.NA
        avg_memory = pd.NA
        max_memory = pd.NA

    return {
        'date': date,
        'successful': successful,
        'duration': duration,
        'avg_memory': avg_memory,
        'max_memory': max_memory,
        'note': note,
    }


def parse_execution_info(entry):
    # read data
    txt = entry.read_text()

    # gather stats
    rules = ','.join(sorted(set(re.findall('rule (.*):', txt))))
    wildcards = ','.join(sorted(set(re.findall('wildcards: (.*)', txt))))

    return {
        'rules': rules,
        'wildcards': wildcards,
    }


def main(root, fname_out):
    tmp = []
    for child in tqdm(walk(root)):
        if child.suffix != '.out':
            continue

        # extract info
        try:
            cluster_info = parse_cluster_info(child)
            execution_info = parse_execution_info(child.with_suffix('.err'))
        except Exception as e:
            cluster_info = {}
            execution_info = {}

            # print(child, e)

        # save results
        tmp.append(
            {
                'filename': child.name,
                **cluster_info,
                **execution_info,
            }
        )

    df = pd.DataFrame(tmp)
    df['date'] = pd.to_datetime(df['date'])

    df.to_csv(fname_out, index=False)
