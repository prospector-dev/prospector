from pathlib import Path
from unittest import TestCase

from prospector.finder import FileFinder

_TEST_DATA = Path(__file__).parent / "testdata"


class TestFileFinder(TestCase):
    def test_python_in_normal_dir(self):
        """
        This test is to find packages and files when given a directory which
        is not itself a python module but contains python modules
        """
        finder = FileFinder(_TEST_DATA / "test1" / "somedir")

        found = list(finder.python_modules)
        self.assertEqual(1, len(found))
        self.assertEqual("__init__.py", found[0].name)
        self.assertEqual("package2", found[0].parent.name)

    def test_directory_with_modules(self):
        """
        Tests a non-module directory containing python modules finds all modules and
        files correctly
        """
        finder = FileFinder(_TEST_DATA / "test3")

        self.assertEqual(4, len(finder.files))
        self.assertEqual(4, len(finder.python_modules))
        self.assertEqual(4, len(finder.python_packages))

    def test_package_finder(self):
        """
        Checks that packages are found correctly and all - including subpackages if asked - are listed
        """
        finder = FileFinder(_TEST_DATA / "test2")
        self.assertEqual(2, len(finder.python_packages))

        finder = FileFinder(_TEST_DATA / "test3")
        self.assertEqual(4, len(finder.python_packages))

        finder = FileFinder(_TEST_DATA / "test4")
        self.assertEqual(3, len(finder.python_packages))

    def test_subdirectories_omitted_if_parent_excluded(self):
        """
        Verifies that if the directory "b" in "a/b/c/d" is ignored, then so are all children
        """
        finder = FileFinder(_TEST_DATA / "filter_test", exclusion_filters=[lambda p: p.name == "ignore_me"])
        self.assertEqual(1, len(finder.python_modules))
        lvl2 = _TEST_DATA / "filter_test/ignore_me/level2"
        self.assertNotIn(lvl2, finder.directories)
        self.assertNotIn(lvl2, finder.python_modules)

    def test_workdir_set(self):
        """
        Simple test to validate args/kwargs are working as expected
        """
        search = (
            _TEST_DATA / "test1",
            _TEST_DATA / "test3",
            _TEST_DATA / "test3",
        )
        finder = FileFinder(*search)
        self.assertIsNotNone(finder.workdir)

        finder = FileFinder(*search, workdir=_TEST_DATA)
        self.assertEqual(_TEST_DATA, finder.workdir)

    def test_multiple_search_directories(self):
        """
        The other tests only gave the finder one directory - this test gives it more,
        and checks there are no duplicates
        """
        search = (
            _TEST_DATA / "test1",
            _TEST_DATA / "test3",
            _TEST_DATA / "test3",
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

    def test_non_existent_path(self):
        """
        Checks that the finder can cleanly handle being given paths that do not exist
        """
        self.assertRaises(FileNotFoundError, FileFinder, _TEST_DATA / "does_not_exist")

    def test_exclusion_filters(self):
        """
        Checks that paths excluded by filters are not returned in lists
        """
        # exclude everything
        finder = FileFinder(_TEST_DATA, exclusion_filters=[lambda _: True])

        self.assertEqual(0, len(finder.files))
        self.assertEqual(0, len(finder.python_modules))
        self.assertEqual(0, len(finder.python_packages))
        self.assertEqual(0, len(finder.directories))

        # exclude anything under 'package1'
        pkg1 = Path(_TEST_DATA / "test1" / "package1")

        def exclude(p: Path):
            return "package1" in p.parts

        finder = FileFinder(_TEST_DATA / "test1", exclusion_filters=[exclude])
        modules = finder.python_modules
        self.assertNotIn(pkg1, modules)
