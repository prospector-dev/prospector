# -*- coding: utf-8 -*-
import sys
from unittest import SkipTest, TestCase

from prospector.message import Location, Message

if sys.version_info >= (3, 0):
    from unittest import mock
else:
    import mock


try:
    from prospector.tools.mypy import MypyTool, format_message
except ImportError:
    raise SkipTest


class TestMypyTool(TestCase):
    def test_format_message_with_character(self):
        location = Location(
            path="file.py", module=None, function=None, line=17, character=2
        )
        expected = Message(
            source="mypy", code="error", location=location, message="Important error"
        )
        self.assertEqual(
            format_message("file.py:17:2: error: Important error"), expected
        )

    def test_format_message_without_character_and_columns_in_message(self):
        location = Location(
            path="file.py", module=None, function=None, line=17, character=None
        )
        expected = Message(
            source="mypy", code="note", location=location, message="Important error"
        )
        self.assertEqual(
            format_message('file.py:17: note: unused "type: ignore" comment'), expected
        )

    def test_format_message_without_character(self):
        location = Location(
            path="file.py", module=None, function=None, line=17, character=None
        )
        expected = Message(
            source="mypy", code="error", location=location, message="Important error"
        )
        self.assertEqual(format_message("file.py:17: error: Important error"), expected)

    def test_pre730_format(self):
        tool = MypyTool()
        found_files = mock.MagicMock()
        output = ['file.py:17: error: Important error', 'file.py:17:2: error: Important error']

        with mock.patch('mypy.api.run') as mock_mypy:
            mock_mypy.return_value = ('\n'.join(output), "unused")
            messages = tool.run(found_files)

        self.assertEqual(len(messages), len(output))

    def test_pre730_format_empty(self):
        tool = MypyTool()
        found_files = mock.MagicMock()
        output = []

        with mock.patch('mypy.api.run') as mock_mypy:
            mock_mypy.return_value = ('\n'.join(output), "unused")
            messages = tool.run(found_files)

        self.assertEqual(len(messages), len(output))

    def test_post730_format(self):
        tool = MypyTool()
        found_files = mock.MagicMock()
        output = ['file.py:17: error: Important error', 'file.py:17:2: error: Important error', 'Found 2 errors in 1 file (checked 63 source files)']

        with mock.patch('mypy.api.run') as mock_mypy:
            mock_mypy.return_value = ('\n'.join(output), "unused")
            messages = tool.run(found_files)

        self.assertEqual(len(messages), len(output) - 1)

    def test_post730_format_empty(self):
        tool = MypyTool()
        found_files = mock.MagicMock()
        output = ['Success: no issues found in 9 source files']

        with mock.patch('mypy.api.run') as mock_mypy:
            mock_mypy.return_value = ('\n'.join(output), "unused")
            messages = tool.run(found_files)

        self.assertEqual(len(messages), len(output) - 1)
