r"""
Each tool has its own method of ignoring errors and warnings.
For example, pylint requires a comment of the form

    # pylint disable=<error codes>

PEP8 will not warn on lines with

    # noqa

Additionally, flake8 follows that convention for pyflakes errors,
but pyflakes itself does not.

Finally, an entire file is ignored by flake8 if this line is found
in the file:

    # flake8\: noqa       (the \ is needed to stop prospector ignoring this file :))

This module's job is to attempt to collect all of these methods into
a single coherent list of error suppression locations.
"""

import re
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Optional

from prospector import encoding
from prospector.config import ProspectorConfig
from prospector.exceptions import FatalProspectorException
from prospector.message import Message

_FLAKE8_IGNORE_FILE = re.compile(r"flake8[:=]\s*noqa", re.IGNORECASE)
_PEP8_IGNORE_LINE = re.compile(r"#\s+noqa", re.IGNORECASE)
_PYLINT_SUPPRESSED_MESSAGE = re.compile(r"^Suppressed \'([a-z0-9-]+)\' \(from line \d+\)$")


def get_noqa_suppressions(file_contents: list[str], noqa: bool = True, flake8: bool = True) -> tuple[bool, set[int]]:
    """
    Finds all pep8/flake8 suppression messages

    :param file_contents:
        A list of file lines
    :return:
        A pair - the first is whether to ignore the whole file, the
        second is a set of (0-indexed) line numbers to ignore.
    """
    ignore_whole_file = False
    ignore_lines = set()
    for line_number, line in enumerate(file_contents):
        if flake8 and _FLAKE8_IGNORE_FILE.search(line):
            ignore_whole_file = True
        if noqa and _PEP8_IGNORE_LINE.search(line):
            ignore_lines.add(line_number + 1)

    return ignore_whole_file, ignore_lines


_PYLINT_EQUIVALENTS = {
    # TODO: blending has this info already?
    "unused-import": (
        ("pyflakes", "FL0001"),
        ("frosted", "E101"),
    )
}


def _parse_pylint_informational(
    messages: list[Message],
) -> tuple[set[Optional[Path]], dict[Optional[Path], dict[int, list[str]]]]:
    ignore_files: set[Optional[Path]] = set()
    ignore_messages: dict[Optional[Path], dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))

    for message in messages:
        if message.source == "pylint":
            if message.code == "suppressed-message":
                # this is a message indicating that a message was raised
                # by pylint but suppressed by configuration in the file
                match = _PYLINT_SUPPRESSED_MESSAGE.match(message.message)
                if not match:
                    raise FatalProspectorException(f"Could not parsed suppressed message from {message.message}")
                suppressed_code = match.group(1)
                line_dict = ignore_messages[message.location.path]
                assert message.location.line is not None
                line_dict[message.location.line].append(suppressed_code)
            elif message.code == "file-ignored":
                ignore_files.add(message.location.path)
    return ignore_files, ignore_messages


def get_suppressions(
    filepaths: list[Path], messages: list[Message], config: ProspectorConfig
) -> tuple[set[Optional[Path]], dict[Path, set[int]], dict[Optional[Path], dict[int, set[tuple[str, str]]]]]:
    """
    Given every message which was emitted by the tools, and the
    list of files to inspect, create a list of files to ignore,
    and a map of filepath -> line-number -> codes to ignore
    """
    paths_to_ignore: set[Optional[Path]] = set()
    lines_to_ignore: dict[Path, set[int]] = defaultdict(set)
    messages_to_ignore: dict[Optional[Path], dict[int, set[tuple[str, str]]]] = defaultdict(lambda: defaultdict(set))

    conf = config.profile.suppression
    # First deal with 'noqa' style messages
    for filepath in filepaths:
        try:
            file_contents = encoding.read_py_file(filepath).split("\n")
        except encoding.CouldNotHandleEncoding as err:
            # TODO: this output will break output formats such as JSON
            warnings.warn(f"{err.path}: {err.__cause__}", ImportWarning, stacklevel=2)
            continue

        (
            ignore_file,
            ignore_lines,
        ) = get_noqa_suppressions(file_contents, conf.get("noqa", True), conf.get("flake8", True))
        if ignore_file:
            paths_to_ignore.add(filepath)
        lines_to_ignore[filepath] |= ignore_lines

    # Now figure out which messages were suppressed by pylint
    pylint_ignore_files, pylint_ignore_messages = _parse_pylint_informational(messages)
    paths_to_ignore |= pylint_ignore_files
    for pylint_filepath, line_codes in pylint_ignore_messages.items():
        for line_number, codes in line_codes.items():
            for code in codes:
                messages_to_ignore[pylint_filepath][line_number].add(("pylint", code))
                if code in _PYLINT_EQUIVALENTS:
                    for ignore_source, ignore_code in _PYLINT_EQUIVALENTS[code]:
                        messages_to_ignore[pylint_filepath][line_number].add((ignore_source, ignore_code))

    return paths_to_ignore, lines_to_ignore, messages_to_ignore
