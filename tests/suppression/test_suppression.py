import os
import unittest
from pathlib import Path

from prospector.suppression import get_noqa_suppressions
from tests.utils import patch_workdir_argv


class SuppressionTest(unittest.TestCase):
    def _get_file_contents(self, name):
        path = os.path.join(os.path.dirname(__file__), "testdata", name)
        with open(path) as testfile:
            return testfile.readlines()

    def test_ignore_file(self):
        file_contents = self._get_file_contents("test_ignore_file/test.py")
        whole_file, _ = get_noqa_suppressions(file_contents)
        self.assertTrue(whole_file)

    def test_ignore_lines(self):
        file_contents = self._get_file_contents("test_ignore_lines/test.py")
        _, lines = get_noqa_suppressions(file_contents)
        self.assertSetEqual({1, 2, 3}, lines)

    def test_ignore_enum_error(self):
        file_contents = self._get_file_contents("test_ignore_enum/test.py")
        _, lines = get_noqa_suppressions(file_contents)
        self.assertSetEqual({5}, lines)

    def test_filter_messages(self):
        with patch_workdir_argv(
            workdir=Path(__file__).parent / "testdata/test_filter_messages",
        ) as pros:
            self.assertEqual(0, pros.summary["message_count"])

    def test_filter_messages_negative(self):
        with patch_workdir_argv(
            workdir=Path(__file__).parent / "testdata/test_filter_messages_negative",
        ) as pros:
            self.assertEqual(5, pros.summary["message_count"])
