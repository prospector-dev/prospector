import re
from pathlib import Path
from typing import TYPE_CHECKING

from prospector.tools.base import ToolBase

try:  # Python >= 3.11
    import re._constants as sre_constants
except ImportError:
    import sre_constants  # pylint: disable=deprecated-module

import yaml

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.profiles import AUTO_LOADED_PROFILES

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


PROFILE_IS_EMPTY = "profile-is-empty"
CONFIG_SETTING_SHOULD_BE_LIST = "should-be-list"
CONFIG_UNKNOWN_SETTING = "unknown-setting"
CONFIG_SETTING_MUST_BE_INTEGER = "should-be-int"
CONFIG_SETTING_MUST_BE_BOOL = "should-be-bool"
CONFIG_INVALID_VALUE = "invalid-value"
CONFIG_INVALID_REGEXP = "invalid-regexp"
CONFIG_DEPRECATED_SETTING = "deprecated"
CONFIG_DEPRECATED_CODE = "deprecated-tool-code"

__all__ = ("ProfileValidationTool",)


def _tool_names(with_deprecated: bool = True) -> list[str]:
    from prospector.tools import DEPRECATED_TOOL_NAMES, TOOLS  # pylint: disable=import-outside-toplevel

    tools = list(TOOLS)
    if with_deprecated:
        tools += DEPRECATED_TOOL_NAMES.keys()
    return tools


class ProfileValidationTool(ToolBase):
    LIST_SETTINGS = ("inherits", "uses", "ignore", "ignore-paths", "ignore-patterns")
    BOOL_SETTINGS = ("doc-warnings", "test-warnings", "autodetect")
    OTHER_SETTINGS = (
        "strictness",
        "max-line-length",
        "output-format",
        "output-target",
        "member-warnings",
        "pep8",
        # bit of a grim hack; prospector does not use the following but Landscape does:
        # TODO: think of a better way to avoid Landscape-specific config leaking into prospector
        "python-targets",
    )
    ALL_SETTINGS = LIST_SETTINGS + BOOL_SETTINGS + OTHER_SETTINGS

    def __init__(self) -> None:
        self.to_check = set(AUTO_LOADED_PROFILES)
        self.ignore_codes: list[str] = []

    def configure(self, prospector_config: "ProspectorConfig", found_files: FileFinder) -> None:
        for profile in prospector_config.config.profiles:
            self.to_check.add(profile)

        self.ignore_codes = prospector_config.get_disabled_messages("profile-validator")

    def validate(self, filepath: Path) -> list[Message]:
        # pylint: disable=too-many-locals
        # TODO: this should be broken down into smaller pieces
        messages: list[Message] = []

        with filepath.open() as profile_file:
            _file_contents = profile_file.read()
            parsed = yaml.safe_load(_file_contents)
            raw_contents = _file_contents.split("\n")

        def add_message(code: str, message: str, setting: str) -> None:
            if code in self.ignore_codes:
                return
            line = -1
            for number, fileline in enumerate(raw_contents):
                if setting in fileline:
                    line = number + 1
                    break
            location = Location(filepath, None, None, line, 0)
            messages.append(Message("profile-validator", code, location, message))

        if parsed is None:
            # this happens if a completely empty profile is found
            add_message(
                PROFILE_IS_EMPTY,
                f"{filepath} is a completely empty profile",
                "entire-file",
            )
            return messages

        for setting in ProfileValidationTool.BOOL_SETTINGS:
            if not isinstance(parsed.get(setting, False), bool):
                add_message(
                    CONFIG_SETTING_MUST_BE_BOOL,
                    f'"{setting}" should be true or false',
                    setting,
                )

        if not isinstance(parsed.get("max-line-length", 0), int):
            add_message(
                CONFIG_SETTING_MUST_BE_INTEGER,
                '"max-line-length" should be an integer',
                "max-line-length",
            )

        if "strictness" in parsed:
            possible_strictness = ("veryhigh", "high", "medium", "low", "verylow", "none")
            if parsed["strictness"] not in possible_strictness:
                _joined = ", ".join(possible_strictness)
                add_message(
                    CONFIG_INVALID_VALUE,
                    f'"strictness" must be one of {_joined}',
                    "strictness",
                )

        if "uses" in parsed:
            possible_libs = ("django", "celery", "flask")
            parsed_list = parsed["uses"] if isinstance(parsed["uses"], list) else [parsed["uses"]]
            for uses in parsed_list:
                if uses not in possible_libs:
                    _joined = ", ".join(possible_libs)
                    add_message(
                        CONFIG_INVALID_VALUE,
                        f'"{uses}" is not valid for "uses", must be one of {_joined}',
                        uses,
                    )

        if "ignore" in parsed:
            add_message(
                CONFIG_DEPRECATED_SETTING,
                '"ignore" is deprecated, please update to use "ignore-patterns" instead',
                "ignore",
            )

        if "python-targets" in parsed:
            python_targets = (
                parsed["python-targets"] if isinstance(parsed["python-targets"], list) else [parsed["python-targets"]]
            )

            for target in python_targets:
                if str(target) not in ("2", "3"):
                    add_message(
                        CONFIG_INVALID_VALUE,
                        f'"{target}" is not valid for "python-targets", must be either 2 or 3',
                        str(target),
                    )

        for pattern in parsed.get("ignore-patterns", []):
            try:
                re.compile(pattern)
            except sre_constants.error:
                add_message(CONFIG_INVALID_REGEXP, "Invalid regular expression", pattern)

        for key in ProfileValidationTool.LIST_SETTINGS:
            if key not in parsed:
                continue
            if not isinstance(parsed[key], (tuple, list)):
                add_message(CONFIG_SETTING_SHOULD_BE_LIST, f'"{key}" should be a list', key)

        for key in parsed:
            if key not in ProfileValidationTool.ALL_SETTINGS and key not in _tool_names():
                add_message(
                    CONFIG_UNKNOWN_SETTING,
                    f'"{key}" is not a valid prospector setting',
                    key,
                )

        if "pep257" in parsed:
            add_message(
                CONFIG_DEPRECATED_CODE,
                "pep257 tool has been renamed to 'pydocstyle'. The name pep257 will be removed in prospector 2.0+.",
                "pep257",
            )

        if "pep8" in parsed:
            pep8val = parsed["pep8"]
            if isinstance(pep8val, dict):
                add_message(
                    CONFIG_DEPRECATED_CODE,
                    "pep8 tool has been renamed to 'pycodestyle'. "
                    "Using pep8 to configure the tool will be removed in prospector 2.0+.",
                    "pep8",
                )
            elif pep8val not in ("full", "none"):
                add_message(
                    CONFIG_UNKNOWN_SETTING,
                    f"{pep8val} is not a valid setting for pep8 - must be either 'full' or 'none'",
                    "pep8",
                )

        if "pyflakes" in parsed:
            from prospector.tools import pyflakes  # pylint: disable=import-outside-toplevel

            for code in parsed["pyflakes"].get("enable", []) + parsed["pyflakes"].get("disable", []):
                if code in pyflakes.LEGACY_CODE_MAP:
                    _legacy = pyflakes.LEGACY_CODE_MAP[code]
                    add_message(
                        CONFIG_DEPRECATED_CODE,
                        f"Pyflakes {code} was renamed to {_legacy}",
                        "pyflakes",
                    )

        return messages

    def run(self, found_files: FileFinder) -> list[Message]:
        messages = []
        for filepath in found_files.files:
            for possible in self.to_check:
                if filepath == possible:
                    messages += self.validate(filepath)
                    break

        return messages
