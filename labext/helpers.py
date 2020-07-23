from pathlib import Path
from typing import Union


def read_file(infile: Union[str, Path]):
    with open(infile, 'r') as f:
        return f.read()


def identity_func(x):
    return x


def noarg_func():
    pass
