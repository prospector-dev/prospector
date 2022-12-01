import contextlib
from pathlib import Path
from typing import List
from unittest.mock import patch


@contextlib.contextmanager
def patch_cli(*args: List[str]):
    with patch("sys.argv", args):
        yield


@contextlib.contextmanager
def patch_execution(*args: List[str], set_cwd: Path = None):
    """
    Utility to patch builtins to simulate running prospector in a particular directory
    with particular commandline args

    :param set_cwd:  Simulate changing directory into the given directory
    :param args:  Any additional command-line arguments to pass to prospector
    """
    args = ("prospector",) + args
    with patch_cli(*args):
        yield
