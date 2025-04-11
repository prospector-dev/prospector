from __future__ import annotations

import contextlib
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any, Optional
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.run import Prospector


@contextlib.contextmanager
def patch_cli(*args: Any, target: str = "sys.argv") -> Generator[None, None]:
    with patch(target, args):
        yield


@contextlib.contextmanager
def patch_cwd(set_cwd: Path) -> Generator[None, None]:
    # oddness here : Path.cwd() uses os.getcwd() under the hood in python<=3.9 but
    # for python 3.10+, they return different things if only one is patched; therefore,
    # for this test to work in all python versions prospector supports, both need to
    # be patched (or, an "if python version" statement but it's easier to just patch both)
    cwd_str = str(set_cwd.absolute())
    with (
        patch("pathlib.Path.cwd", new=lambda: set_cwd),
        patch("os.getcwd", new=lambda: cwd_str),
        patch("os.curdir", new=cwd_str),
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
def patch_execution(*args: str, set_cwd: Optional[Path] = None) -> Generator[None, None]:
    """
    Utility to patch builtins to simulate running prospector in a particular directory
    with particular commandline args

    :param set_cwd:  Simulate changing directory into the given directory
    :param args:  Any additional command-line arguments to pass to prospector
    """
    args = ("prospector", *args)
    with patch_cli(*args):
        if set_cwd:
            with patch_cwd(set_cwd):
                yield
        else:
            yield


@contextlib.contextmanager
def patch_workdir_argv(
    target: str = "sys.argv", args: list[str] | None = None, workdir: Path | None = None
) -> Generator[Prospector, None]:
    if args is None:
        args = ["prospector"]
    with patch_cli(*args, target=target):
        assert workdir is not None
        config = ProspectorConfig(workdir=workdir)
        config.paths = [workdir]
        pros = Prospector(config)
        pros.execute()
        yield pros
