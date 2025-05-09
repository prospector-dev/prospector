import json
from pathlib import Path
from typing import Any
from unittest import SkipTest, TestCase
from unittest.mock import patch

import pytest

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.exceptions import BadToolConfig

try:
    from prospector.tools.pyright import format_messages
except ImportError:
    raise SkipTest from ImportError  # type: ignore[call-arg] # noqa: B904


class TestPyrightTool(TestCase):
    @staticmethod
    def _get_config(profile_name: str) -> ProspectorConfig:
        profile_path = Path(__file__).parent / f"test_profiles/{profile_name}.yaml"
        with patch("sys.argv", ["prospector", "--profile", str(profile_path.absolute())]):
            return ProspectorConfig()

    def test_unrecognised_options(self) -> None:
        finder = FileFinder(Path(__file__).parent)
        with pytest.raises(BadToolConfig):
            self._get_config("pyright_bad_options").get_tools(finder)

    def test_good_options(self) -> None:
        finder = FileFinder(Path(__file__).parent)
        self._get_config("pyright_good_options").get_tools(finder)


class TestPyrightMessageFormat(TestCase):
    def _encode_messages(self, messages: list[dict[str, Any]]) -> str:
        return json.dumps({"generalDiagnostics": messages})

    def test_format_message_with_character(self) -> None:
        location = Location(path="file.py", module=None, function=None, line=17, character=2)
        expected = Message(source="pyright", code="error", location=location, message="Important error")
        assert format_messages(
            self._encode_messages(
                [
                    {
                        "file": "file.py",
                        "message": "Important error",
                        "rule": "error",
                        "range": {"start": {"line": 17, "character": 2}},
                    }
                ]
            )
        ) == [expected]

    def test_format_message_without_character(self) -> None:
        location = Location(path="file.py", module=None, function=None, line=17, character=-1)
        expected = Message(source="pyright", code="note", location=location, message="Important error")
        assert format_messages(
            self._encode_messages(
                [{"file": "file.py", "message": "Important error", "rule": "note", "range": {"start": {"line": 17}}}]
            )
        ) == [expected]

    def test_format_message_without_line(self) -> None:
        location = Location(path="file.py", module=None, function=None, line=-1, character=-1)
        expected = Message(
            source="pyright",
            code="error",
            location=location,
            message="Important error",
        )
        assert format_messages(
            self._encode_messages([{"file": "file.py", "message": "Important error", "rule": "error"}])
        ) == [expected]
