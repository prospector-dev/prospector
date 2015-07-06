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
