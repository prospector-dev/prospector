from unittest import SkipTest, TestCase

from prospector.message import Location, Message

try:
    from prospector.tools.mypy import format_message
except ImportError:
    raise SkipTest


class TestMypyTool(TestCase):
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
