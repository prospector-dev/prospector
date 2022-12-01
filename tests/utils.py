import contextlib
import sys
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
    cwd_str = str(set_cwd.absolute())
    with patch("pathlib.Path.cwd", new=lambda: set_cwd), patch("os.getcwd", new=lambda: cwd_str), patch(
        "os.curdir", new=cwd_str
    ):
        # Turns out that Python 3.10 added the `getcwd` to the _NormalAccessor instead of falling
        # back on os.getcwd, and so this needs to be patched too...
        if sys.version_info[:2] == (3, 10):
            # sigh...
            with patch("pathlib._NormalAccessor.getcwd", new=lambda _: cwd_str):
                yield
        else:
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
        if set_cwd:
            with patch_cwd(set_cwd):
                yield
        else:
            yield
