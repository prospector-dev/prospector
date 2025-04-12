from pathlib import Path
from unittest import TestCase

import pytest

from prospector.finder import FileFinder

from .utils import TEST_DATA


class TestFileFinder(TestCase):
    def test_python_in_normal_dir(self) -> None:
        """
        This test is to find packages and files when given a directory which
        is not itself a python module but contains python modules
        """
        finder = FileFinder(TEST_DATA / "test1" / "somedir")

        found = list(finder.python_modules)
        assert len(found) == 1
        assert found[0].name == "__init__.py"
        assert found[0].parent.name == "package2"

    def test_directory_with_modules(self) -> None:
        """
        Tests a non-module directory containing python modules finds all modules and
        files correctly
        """
        finder = FileFinder(TEST_DATA / "test3")

        assert len(finder.files) == 4
        assert all(p.is_absolute() for p in finder.files)

        assert len(finder.python_modules) == 4
        assert all(p.is_absolute() for p in finder.python_modules)

        assert len(finder.python_packages) == 4
        assert all(p.is_absolute() for p in finder.python_packages)

    def test_package_finder(self) -> None:
        """
        Checks that packages are found correctly and all - including subpackages if asked - are listed
        """
        finder = FileFinder(TEST_DATA / "test2")
        assert len(finder.python_packages) == 2

        finder = FileFinder(TEST_DATA / "test3")
        assert len(finder.python_packages) == 4

        finder = FileFinder(TEST_DATA / "test4")
        assert len(finder.python_packages) == 3

    def test_subdirectories_omitted_if_parent_excluded(self) -> None:
        """
        Verifies that if the directory "b" in "a/b/c/d" is ignored, then so are all children
        """
        finder = FileFinder(TEST_DATA / "filter_test", exclusion_filters=[lambda p: p.name == "ignore_me"])
        assert len(finder.python_modules) == 1
        lvl2 = TEST_DATA / "filter_test/ignore_me/level2"
        assert lvl2 not in finder.directories
        assert lvl2 not in finder.python_modules

    def test_multiple_search_directories(self) -> None:
        """
        The other tests only gave the finder one directory - this test gives it more,
        and checks there are no duplicates
        """
        search = (
            TEST_DATA / "test1",
            TEST_DATA / "test3",
            TEST_DATA / "test3",
        )
        finder = FileFinder(*search)

        files = finder.files
        assert len(files) == 6

        modules = finder.python_modules
        assert len(modules) == 6

        packages = finder.python_packages
        assert len(packages) == 6

        dirs = finder.directories
        # note: 10 including the 'test1' and 'test3' directories themselves, which contain 8 in total
        assert len(dirs) == 10

    def test_non_existent_path(self) -> None:
        """
        Checks that the finder can cleanly handle being given paths that do not exist
        """
        with pytest.raises(FileNotFoundError):
            FileFinder(TEST_DATA / "does_not_exist")

    def test_exclusion_filters(self) -> None:
        """
        Checks that paths excluded by filters are not returned in lists
        """
        # exclude everything
        finder = FileFinder(TEST_DATA, exclusion_filters=[lambda _: True])

        assert len(finder.files) == 0
        assert len(finder.python_modules) == 0
        assert len(finder.python_packages) == 0
        assert len(finder.directories) == 0

        # exclude anything under 'package1'
        pkg1 = Path(TEST_DATA / "test1" / "package1")

        def exclude(p: Path) -> bool:
            return "package1" in p.parts

        finder = FileFinder(TEST_DATA / "test1", exclusion_filters=[exclude])
        modules = finder.python_modules
        assert pkg1 not in modules
