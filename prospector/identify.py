# Largely inspired by https://github.com/pre-commit/identify/blob/main/identify/identify.py#L178

import errno
import os
import shlex
import string
from pathlib import Path
from typing import IO

printable = frozenset(string.printable)


def _shebang_split(line: str) -> tuple[str, ...]:
    try:
        # shebangs aren't supposed to be quoted, though some tools such as
        # setuptools will write them with quotes so we'll best-guess parse
        # with shlex first
        return tuple(shlex.split(line))
    except ValueError:
        # failing that, we'll do a more "traditional" shebang parsing which
        # just involves splitting by whitespace
        return tuple(line.split())


def _parse_nix_shebang(
    bytes_io: IO[bytes],
    cmd: tuple[str, ...],
) -> tuple[str, ...]:
    while bytes_io.read(2) == b"#!":
        next_line_b = bytes_io.readline()
        try:
            next_line = next_line_b.decode("UTF-8")
        except UnicodeDecodeError:
            return cmd

        for c in next_line:
            if c not in printable:
                return cmd

        line_tokens = _shebang_split(next_line.strip())
        for i, token in enumerate(line_tokens[:-1]):
            if token != "-i":  # noqa: S105
                continue
            # The argument to -i flag
            cmd = (line_tokens[i + 1],)
    return cmd


def _parse_shebang(bytes_io: IO[bytes]) -> tuple[str, ...]:
    """Parse the shebang from a file opened for reading binary."""
    if bytes_io.read(2) != b"#!":
        return ()
    first_line_b = bytes_io.readline()
    try:
        first_line = first_line_b.decode("UTF-8")
    except UnicodeDecodeError:
        return ()

    # Require only printable ascii
    for c in first_line:
        if c not in printable:
            return ()

    cmd = _shebang_split(first_line.strip())
    if cmd[:2] == ("/usr/bin/env", "-S"):
        cmd = cmd[2:]
    elif cmd[:1] == ("/usr/bin/env",):
        cmd = cmd[1:]

    if cmd == ("nix-shell",):
        return _parse_nix_shebang(bytes_io, cmd)

    return cmd


def parse_shebang_from_file(path: Path) -> tuple[str, ...]:
    """Parse the shebang given a file path."""
    if not path.exists():
        return ()
    if not os.access(path, os.X_OK):
        return ()

    try:
        with path.open("rb") as f:
            return _parse_shebang(f)
    except OSError as e:
        if e.errno == errno.EINVAL:
            return ()
        else:
            raise
