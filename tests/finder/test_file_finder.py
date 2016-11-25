import os
from unittest import TestCase
from prospector.finder import find_python, FoundFiles, SingleFiles
from prospector.pathutils import is_virtualenv


class TestSysPath(TestCase):

    def _run_test(self, name, expected):
        root = os.path.join(os.path.dirname(__file__), 'testdata', name)
        files = find_python([], [root], explicit_file_mode=False)

        expected = [os.path.join(root, e).rstrip(os.path.sep) for e in expected]
        actual = files.get_minimal_syspath()

        expected.sort(key=lambda x: len(x))

        self.assertEqual(actual, expected)

    def test1(self):
        self._run_test('test1', ['', 'somedir'])

    def test2(self):
        self._run_test('test2', [''])

    def test3(self):
        self._run_test('test3', ['package'])


class TestVirtualenvDetection(TestCase):

    def test_is_a_venv(self):
        path = os.path.join(os.path.dirname(__file__), 'testdata', 'venvs', 'is_a_venv')
        self.assertTrue(is_virtualenv(path))

    def test_not_a_venv(self):
        path = os.path.join(os.path.dirname(__file__), 'testdata', 'venvs', 'not_a_venv')
        self.assertFalse(is_virtualenv(path))

    def test_long_path_not_a_venv(self):
        """
        Windows doesn't allow extremely long paths. This unit test has to be
        run in Windows to be meaningful, though it shouldn't fail in other
        operating systems.
        """
        path = [os.path.dirname(__file__), 'testdata', 'venvs']
        path.extend(['long_path_not_a_venv'] * 14)
        path.append('long_path_not_a_venv_long_path_not_a_v')
        path = os.path.join(*path)
        self.assertFalse(is_virtualenv(path))


class TestPathFinderDir(TestCase):

    def _run_test(self, expected, method_under_test):
        # method_under_test: unbound FoundFiles method 
        root = os.path.join(
            os.path.dirname(__file__), 'testdata', 'dirs_mods_packages')
        found = find_python(
            ignores=[], paths=[root], explicit_file_mode=False)

        expected = [os.path.normpath(os.path.join(root, e)) for e in expected]
        expected.sort()
        actual = list(method_under_test(found))
        actual.sort()
        self.assertEqual(actual, expected)

    def test_file_paths(self):
        expected = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        self._run_test(expected, FoundFiles.iter_file_paths)

    def test_module_paths(self):
        expected = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/package_module1.py',
            'package/package_module2.py',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'module1.py',
            'module2.py',
            ]
        self._run_test(expected, FoundFiles.iter_module_paths)

    def test_directory_paths(self):
        expected = [
            'package',
            'package/subpackage',
            'nonpackage',
            ]
        self._run_test(expected, FoundFiles.iter_directory_paths)

    def test_package_paths(self):
        expected = [
            'package',
            'package/subpackage',
            ]
        self._run_test(expected, FoundFiles.iter_package_paths)


class TestPathFinderSingleFiles(TestCase):

    def _run_test(self, paths, expected, method_under_test):
        # method_under_test: unbound SingleFiles method 
        root = os.path.join(
            os.path.dirname(__file__), 'testdata', 'dirs_mods_packages')
        paths = [os.path.normpath(os.path.join(root, p)) for p in paths]
        found = find_python(
            ignores=[], paths=paths, explicit_file_mode=True)
        expected = [os.path.normpath(os.path.join(root, e)) for e in expected]
        expected.sort()
        actual = list(method_under_test(found))
        actual.sort()
        self.assertEqual(actual, expected)

    def test_file_paths(self):
        paths = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        expected = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        self._run_test(paths, expected, SingleFiles.iter_file_paths)

    def test_module_paths(self):
        paths = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        # SingleFiles.iter_module_paths yields all file paths, not just Python
        # modules
        expected = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        self._run_test(paths, expected, SingleFiles.iter_module_paths)

    def test_directory_paths(self):
        paths = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        # SingleFiles.iter_directory_paths yields the directories of all file
        # paths (duplicates are not filtered)
        expected = [
            'package',
            'package/subpackage',
            'package/subpackage',
            'package/subpackage',
            'package/subpackage',
            'package',
            'package',
            'package',
            'nonpackage',
            'nonpackage',
            'nonpackage',
            '',
            '',
            '',
            ]
        self._run_test(paths, expected, SingleFiles.iter_directory_paths)

    def test_package_paths(self):
        paths = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        # SingleFiles.iter_package_paths yields all file paths, not just Python
        # packages
        expected = [
            'package/__init__.py',
            'package/subpackage/__init__.py',
            'package/subpackage/subpackage_module1.py',
            'package/subpackage/subpackage_module2.py',
            'package/subpackage/subpackage_plain.txt',
            'package/package_module1.py',
            'package/package_module2.py',
            'package/package_plain.txt',
            'nonpackage/nonpackage_module1.py',
            'nonpackage/nonpackage_module2.py',
            'nonpackage/nonpackage_plain.txt',
            'module1.py',
            'module2.py',
            'plain.txt',
            ]
        self._run_test(paths, expected, SingleFiles.iter_package_paths)


