from pathlib import Path
from unittest import SkipTest, TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import find_python
from prospector.message import Location, Message
from prospector.tools.exceptions import BadToolConfig

try:
    from prospector.tools.mypy import format_message
except ImportError:
    raise SkipTest


class TestMypyTool(TestCase):
    @staticmethod
    def _get_config(profile_name: str) -> ProspectorConfig:
        profile_path = Path(__file__).parent / f"test_profiles/{profile_name}.yaml"
        with patch("sys.argv", ["prospector", "--profile", str(profile_path.absolute())]):
            return ProspectorConfig()

    def test_unrecognised_options(self):
        finder = find_python([], [], True, Path(__file__).parent.absolute())
        self.assertRaises(BadToolConfig, self._get_config("mypy_bad_options").get_tools, finder)

    def test_good_options(self):
        finder = find_python([], [], True, Path(__file__).parent.absolute())
        self._get_config("mypy_good_options").get_tools(finder)


class TestMypyMessageFormat(TestCase):
    def test_format_message_with_character(self):
        location = Location(path="file.py", module=None, function=None, line=17, character=2)
        expected = Message(source="mypy", code="error", location=location, message="Important error")
        self.assertEqual(format_message("file.py:17:2: error: Important error"), expected)

    def test_format_message_without_character_and_columns_in_message(self):
        location = Location(path="file.py", module=None, function=None, line=17, character=None)
        expected = Message(source="mypy", code="note", location=location, message="Important error")
        self.assertEqual(format_message('file.py:17: note: unused "type: ignore" comment'), expected)

    def test_format_message_without_character(self):
        location = Location(path="file.py", module=None, function=None, line=17, character=None)
        expected = Message(source="mypy", code="error", location=location, message="Important error")
        self.assertEqual(format_message("file.py:17: error: Important error"), expected)

    def test_format_dupplicated_module_win(self):
        location = Location(path="file.py", module=None, function=None, line=0, character=None)
        expected = Message(
            source="mypy",
            code="error",
            location=location,
            message="Duplicate module named 'file' (also at 'C:\\Repositories\\file.py')",
        )
        self.assertEqual(
            format_message("file.py: error: Duplicate module named 'file' (also at 'C:\\Repositories\\file.py')"),
            expected,
        )

    def test_format_dupplicated_module_linux(self):
        location = Location(path="file.py", module=None, function=None, line=0, character=None)
        expected = Message(
            source="mypy",
            code="error",
            location=location,
            message="Duplicate module named 'file' (also at '/Repositories/file.py')",
        )
        self.assertEqual(
            format_message("file.py: error: Duplicate module named 'file' (also at '/Repositories/file.py')"),
            expected,
        )
