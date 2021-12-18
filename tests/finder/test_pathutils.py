from pathlib import Path
from unittest import TestCase

from prospector.pathutils import is_python_module, is_python_package, is_virtualenv

_TEST_DATA = Path(__file__).parent / "testdata"


class TestFinderUtils(TestCase):
    def test_is_python_package(self):
        this_dir = Path(__file__).parent
        self.assertTrue(is_python_package(this_dir))
        self.assertFalse(is_python_package(_TEST_DATA / "not_a_package"))
        self.assertFalse(is_python_package(_TEST_DATA / "not_a_package" / "placeholder.txt"))

    def test_is_python(self):
        self.assertFalse(is_python_module(_TEST_DATA / "not_a_package" / "placeholder.txt"))
        self.assertTrue(is_python_module(Path(__file__)))


class TestVirtualenvDetection(TestCase):
    def test_is_a_venv(self):
        path = _TEST_DATA / "venvs" / "is_a_venv"
        self.assertTrue(is_virtualenv(path))

    def test_not_a_venv(self):
        path = _TEST_DATA / "venvs" / "not_a_venv"
        self.assertFalse(is_virtualenv(path))

    def test_long_path_not_a_venv(self):
        """
        Windows doesn't allow extremely long paths. This unit test has to be
        run in Windows to be meaningful, though it shouldn't fail in other
        operating systems.
        """
        path = _TEST_DATA / "venvs" / "is_a_venv"
        for _ in range(14):
            path /= "long_path_not_a_venv"
        path /= "long_path_not_a_venv_long_path_not_a_v"
        self.assertFalse(is_virtualenv(path))
