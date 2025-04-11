import os
import unittest
from pathlib import Path

from prospector.suppression import get_noqa_suppressions
from tests.utils import patch_workdir_argv


class SuppressionTest(unittest.TestCase):
    def _get_file_contents(self, name: str) -> list[str]:
        path = os.path.join(os.path.dirname(__file__), "testdata", name)
        with open(path) as testfile:
            return testfile.readlines()

    def test_ignore_file(self) -> None:
        file_contents = self._get_file_contents("test_ignore_file/test.py")
        whole_file, _, _ = get_noqa_suppressions(file_contents)
        self.assertTrue(whole_file)

    def test_ignore_lines(self) -> None:
        file_contents = self._get_file_contents("test_ignore_lines/test.py")
        _, lines, messages_to_ignore = get_noqa_suppressions(file_contents)
        self.assertSetEqual({1, 2, 3, 4}, lines)

        assert set(messages_to_ignore.keys()) == {6, 7, 8}
        l6 = messages_to_ignore[6].pop()
        assert l6.source is None
        assert l6.code == "code"
        l7 = messages_to_ignore[7].pop()
        assert l7.source is None
        assert l7.code == "code"
        l8_sorted = sorted(messages_to_ignore[8], key=lambda x: x.code)
        l8a = l8_sorted.pop()
        assert l8a.source is None
        assert l8a.code == "code2"
        l8a = l8_sorted.pop()
        assert l8a.source is None
        assert l8a.code == "code1"

    def test_ignore_enum_error(self) -> None:
        file_contents = self._get_file_contents("test_ignore_enum/test.py")
        _, lines, _ = get_noqa_suppressions(file_contents)
        self.assertSetEqual({5}, lines)

    def test_filter_messages(self) -> None:
        with patch_workdir_argv(
            target="setoptconf.source.commandline.sys.argv",
            workdir=Path(__file__).parent / "testdata/test_filter_messages",
        ) as pros:
            assert pros.summary is not None
            self.assertEqual(0, pros.summary["message_count"])

    def test_filter_messages_negative(self) -> None:
        with patch_workdir_argv(
            target="setoptconf.source.commandline.sys.argv",
            workdir=Path(__file__).parent / "testdata/test_filter_messages_negative",
        ) as pros:
            assert pros.summary is not None
            self.assertEqual(5, pros.summary["message_count"])
