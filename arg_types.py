import argparse
import pathlib


def directory_path(arg: str) -> pathlib.Path:
    p = pathlib.Path(arg)
    if p.is_dir():
        return p
    else:
        raise argparse.ArgumentTypeError(f'{arg} is not a path to a directory')


def file_path(arg: str) -> pathlib.Path:
    p = pathlib.Path(arg)
    if p.is_file():
        return p
    else:
        raise argparse.ArgumentTypeError(f'{arg} is not a path to a file')
