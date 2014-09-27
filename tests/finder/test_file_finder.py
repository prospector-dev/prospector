import os
from unittest import TestCase
from prospector.finder import FoundFiles, find_python


class TestSysPath(TestCase):

    def _run_test(self, name, expected):
        root = os.path.join(os.path.dirname(__file__), 'testdata', name)
        files = find_python([], root)

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
