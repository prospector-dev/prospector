import os
from unittest import TestCase
from prospector.finder import find_python
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
