from pathlib import Path
from unittest import TestCase

from prospector.pathutils import is_python_module, is_python_package, is_virtualenv

from .utils import TEST_DATA


class TestFinderUtils(TestCase):
    def test_is_python_package(self) -> None:
        this_dir = Path(__file__).parent
        assert is_python_package(this_dir)
        assert not is_python_package(TEST_DATA / "not_a_package")
        assert not is_python_package(TEST_DATA / "not_a_package" / "placeholder.txt")

    def test_is_python(self) -> None:
        assert not is_python_module(TEST_DATA / "not_a_package" / "placeholder.txt")
        assert is_python_module(Path(__file__))


class TestVirtualenvDetection(TestCase):
    def test_is_a_venv(self) -> None:
        path = TEST_DATA / "venvs" / "is_a_venv"
        assert is_virtualenv(path)

    def test_not_a_venv(self) -> None:
        path = TEST_DATA / "venvs" / "not_a_venv"
        assert not is_virtualenv(path)

    def test_long_path_not_a_venv(self) -> None:
        """
        Windows doesn't allow extremely long paths. This unit test has to be
        run in Windows to be meaningful, though it shouldn't fail in other
        operating systems.
        """
        path = TEST_DATA / "venvs" / "is_a_venv"
        for _ in range(14):
            path /= "long_path_not_a_venv"
        path /= "long_path_not_a_venv_long_path_not_a_v"
        assert not is_virtualenv(path)
