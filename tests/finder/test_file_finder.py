import os
from pathlib import Path
from unittest import TestCase

from prospector.finder import find_python
from prospector.pathutils import is_virtualenv

_TEST_DIR = Path(__file__).parent / "testdata"


def _assert_find_files(name, expected, explicit_file_mode=False):
    root = _TEST_DIR / name
    files = find_python([], [str(root)], explicit_file_mode=explicit_file_mode)

    expected = [os.path.relpath(os.path.join(str(root), e).rstrip(os.path.sep)) for e in expected]
    expected.append(files.rootpath)
    actual = files.get_minimal_syspath()

    expected.sort(key=lambda x: len(x))
    assert actual == expected


def test_sys_path():
    _assert_find_files("test1", ["", "somedir"])
    _assert_find_files("test2", [""])
    _assert_find_files("test3", ["package"])


def test_skip_node_modules():
    _assert_find_files("test_node_modules", ["module1"])


class TestVirtualenvDetection(TestCase):
    def test_is_a_venv(self):
        path = os.path.join(os.path.dirname(__file__), "testdata", "venvs", "is_a_venv")
        self.assertTrue(is_virtualenv(path))

    def test_not_a_venv(self):
        path = os.path.join(os.path.dirname(__file__), "testdata", "venvs", "not_a_venv")
        self.assertFalse(is_virtualenv(path))

    def test_long_path_not_a_venv(self):
        """
        Windows doesn't allow extremely long paths. This unit test has to be
        run in Windows to be meaningful, though it shouldn't fail in other
        operating systems.
        """
        path = [os.path.dirname(__file__), "testdata", "venvs"]
        path.extend(["long_path_not_a_venv"] * 14)
        path.append("long_path_not_a_venv_long_path_not_a_v")
        path = os.path.join(*path)
        self.assertFalse(is_virtualenv(path))
