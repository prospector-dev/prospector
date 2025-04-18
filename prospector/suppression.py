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
from prospector.blender import BLEND_COMBOS
from prospector.exceptions import FatalProspectorException
from prospector.message import Message
from prospector.tools.base import PEP8_IGNORE_LINE_CODE, ToolBase

_FLAKE8_IGNORE_FILE = re.compile(r"flake8[:=]\s*noqa", re.IGNORECASE)
_PEP8_IGNORE_LINE = re.compile(r"#\s*noqa(\s*#.*)?$", re.IGNORECASE)
_PYLINT_SUPPRESSED_MESSAGE = re.compile(r"^Suppressed \'([a-z0-9-]+)\' \(from line \d+\)$")


class Ignore:
    source: Optional[str]
    code: str

    def __init__(
        self,
        source: Optional[str],
        code: str,
    ) -> None:
        self.source = source
        self.code = code

    def __str__(self) -> str:
        return self.code if self.source is None else f"{self.source}.{self.code}"

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self}>"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Ignore):
            return False
        return self.code == value.code and self.source == value.source

    def __hash__(self) -> int:
        return hash((self.source, self.code))


def get_noqa_suppressions(file_contents: list[str]) -> tuple[bool, set[int], dict[int, set[Ignore]]]:
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
    messages_to_ignore: dict[int, set[Ignore]] = defaultdict(set)
    for line_number, line in enumerate(file_contents):
        if _FLAKE8_IGNORE_FILE.search(line):
            ignore_whole_file = True
        if _PEP8_IGNORE_LINE.search(line):
            ignore_lines.add(line_number + 1)
        else:
            noqa_match = PEP8_IGNORE_LINE_CODE.search(line)
            if noqa_match:
                prospector_ignore = noqa_match.group(1).strip().split(",")
                prospector_ignore = [elem.strip() for elem in prospector_ignore]
                for code in prospector_ignore:
                    messages_to_ignore[line_number + 1].add(Ignore(None, code))

    return ignore_whole_file, ignore_lines, messages_to_ignore


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


def _process_tool_ignores(
    tools_ignore: dict[Path, dict[int, set[Ignore]]],
    blend_combos_dict: dict[Ignore, set[Ignore]],
    messages_to_ignore: dict[Optional[Path], dict[int, set[Ignore]]],
) -> None:
    for path, lines_ignore in tools_ignore.items():
        for line, ignores in lines_ignore.items():
            for ignore in ignores:
                if ignore in blend_combos_dict:
                    messages_to_ignore[path][line].update(blend_combos_dict[ignore])


def get_suppressions(
    filepaths: list[Path],
    messages: list[Message],
    tools: Optional[dict[str, ToolBase]] = None,
    blending: bool = False,
    blend_combos: Optional[list[list[tuple[str, str]]]] = None,
) -> tuple[set[Optional[Path]], dict[Path, set[int]], dict[Optional[Path], dict[int, set[Ignore]]]]:
    """
    Given every message which was emitted by the tools, and the
    list of files to inspect, create a list of files to ignore,
    and a map of filepath -> line-number -> codes to ignore
    """
    tools = tools or {}
    blend_combos = blend_combos or BLEND_COMBOS
    blend_combos_dict: dict[Ignore, set[Ignore]] = defaultdict(set)
    if blending:
        for combo in blend_combos:
            ignore_combos = {Ignore(tool, code) for tool, code in combo}
            for ignore in ignore_combos:
                blend_combos_dict[ignore] |= ignore_combos

    paths_to_ignore: set[Optional[Path]] = set()
    lines_to_ignore: dict[Path, set[int]] = defaultdict(set)
    messages_to_ignore: dict[Optional[Path], dict[int, set[Ignore]]] = defaultdict(lambda: defaultdict(set))
    tools_ignore: dict[Path, dict[int, set[Ignore]]] = defaultdict(lambda: defaultdict(set))

    # First deal with 'noqa' style messages
    for filepath in filepaths:
        try:
            file_contents = encoding.read_py_file(filepath).split("\n")
        except encoding.CouldNotHandleEncoding as err:
            # TODO: this output will break output formats such as JSON
            warnings.warn(f"{err.path}: {err.__cause__}", ImportWarning, stacklevel=2)
            continue

        ignore_file, ignore_lines, file_messages_to_ignore = get_noqa_suppressions(file_contents)
        if ignore_file:
            paths_to_ignore.add(filepath)
        lines_to_ignore[filepath] |= ignore_lines
        for line, codes_ignore in file_messages_to_ignore.items():
            messages_to_ignore[filepath][line] |= codes_ignore

        if blending:
            for line_number, line_content in enumerate(file_contents):
                for tool_name, tool in tools.items():
                    tool_ignores = tool.get_ignored_codes(line_content)
                    for tool_ignore, offset in tool_ignores:
                        tools_ignore[filepath][line_number + 1 + offset].add(Ignore(tool_name, tool_ignore))

    # Ignore the blending messages
    if blending:
        _process_tool_ignores(tools_ignore, blend_combos_dict, messages_to_ignore)

    # Now figure out which messages were suppressed by pylint
    pylint_ignore_files, pylint_ignore_messages = _parse_pylint_informational(messages)
    paths_to_ignore |= pylint_ignore_files
    for pylint_filepath, line_codes in pylint_ignore_messages.items():
        for line_number, codes in line_codes.items():
            for code in codes:
                ignore = Ignore("pylint", code)
                messages_to_ignore[pylint_filepath][line_number].add(ignore)

    return paths_to_ignore, lines_to_ignore, messages_to_ignore
