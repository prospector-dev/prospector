import contextlib
from pathlib import Path
from typing import List
from unittest.mock import patch


@contextlib.contextmanager
def patch_cli(*args: List[str]):
    with patch("sys.argv", args):
        yield


@contextlib.contextmanager
def patch_cwd(set_cwd: Path):
    # oddness here : Path.cwd() uses os.getcwd() under the hood in python<=3.9 but
    # for python 3.10+, they return different things if only one is patched; therefore,
    # for this test to work in all python versions prospector supports, both need to
    # be patched (or, an "if python version" statement but it's easier to just patch both)
    with patch("pathlib.Path.cwd", new=lambda: set_cwd), \
         patch("os.getcwd", new=lambda: str(set_cwd.absolute())), \
         patch("os.curdir", new=str(set_cwd.absolute())):
        yield


@contextlib.contextmanager
def patch_execution(set_cwd: Path = None, *args: List[str]):
    """
    Utility to patch builtins to simulate running prospector in a particular directory
    with particular commandline args

    :param set_cwd:  Simulate changing directory into the given directory
    :param args:  Any additional command-line arguments to pass to prospector
    """
    args = ('prospector',) + args
    with patch_cli(*args):
        if set_cwd:
            with patch_cwd(set_cwd):
                yield
        else:
            yield
