from pathlib import Path
from unittest import TestCase

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
        self.assertEqual(1, len(found))
        self.assertEqual("__init__.py", found[0].name)
        self.assertEqual("package2", found[0].parent.name)

    def test_directory_with_modules(self) -> None:
        """
        Tests a non-module directory containing python modules finds all modules and
        files correctly
        """
        finder = FileFinder(TEST_DATA / "test3")

        self.assertEqual(4, len(finder.files))
        self.assertTrue(all(p.is_absolute() for p in finder.files))

        self.assertEqual(4, len(finder.python_modules))
        self.assertTrue(all(p.is_absolute() for p in finder.python_modules))

        self.assertEqual(4, len(finder.python_packages))
        self.assertTrue(all(p.is_absolute() for p in finder.python_packages))

    def test_package_finder(self) -> None:
        """
        Checks that packages are found correctly and all - including subpackages if asked - are listed
        """
        finder = FileFinder(TEST_DATA / "test2")
        self.assertEqual(2, len(finder.python_packages))

        finder = FileFinder(TEST_DATA / "test3")
        self.assertEqual(4, len(finder.python_packages))

        finder = FileFinder(TEST_DATA / "test4")
        self.assertEqual(3, len(finder.python_packages))

    def test_subdirectories_omitted_if_parent_excluded(self) -> None:
        """
        Verifies that if the directory "b" in "a/b/c/d" is ignored, then so are all children
        """
        finder = FileFinder(TEST_DATA / "filter_test", exclusion_filters=[lambda p: p.name == "ignore_me"])
        self.assertEqual(1, len(finder.python_modules))
        lvl2 = TEST_DATA / "filter_test/ignore_me/level2"
        self.assertNotIn(lvl2, finder.directories)
        self.assertNotIn(lvl2, finder.python_modules)

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
        self.assertEqual(6, len(files))

        modules = finder.python_modules
        self.assertEqual(6, len(modules))

        packages = finder.python_packages
        self.assertEqual(6, len(packages))

        dirs = finder.directories
        # note: 10 including the 'test1' and 'test3' directories themselves, which contain 8 in total
        self.assertEqual(10, len(dirs))

    def test_non_existent_path(self) -> None:
        """
        Checks that the finder can cleanly handle being given paths that do not exist
        """
        self.assertRaises(FileNotFoundError, FileFinder, TEST_DATA / "does_not_exist")

    def test_exclusion_filters(self) -> None:
        """
        Checks that paths excluded by filters are not returned in lists
        """
        # exclude everything
        finder = FileFinder(TEST_DATA, exclusion_filters=[lambda _: True])

        self.assertEqual(0, len(finder.files))
        self.assertEqual(0, len(finder.python_modules))
        self.assertEqual(0, len(finder.python_packages))
        self.assertEqual(0, len(finder.directories))

        # exclude anything under 'package1'
        pkg1 = Path(TEST_DATA / "test1" / "package1")

        def exclude(p: Path) -> bool:
            return "package1" in p.parts

        finder = FileFinder(TEST_DATA / "test1", exclusion_filters=[exclude])
        modules = finder.python_modules
        self.assertNotIn(pkg1, modules)
