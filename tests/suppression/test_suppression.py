import os
import unittest
from prospector.suppression import get_noqa_suppressions


class SuppressionTest(unittest.TestCase):

    def _get_file_contents(self, name):
        path = os.path.join(os.path.dirname(__file__), 'testdata', name)
        with open(path) as testfile:
            return testfile.readlines()

    def test_ignore_file(self):
        file_contents = self._get_file_contents('test_ignore_file/test.py')
        whole_file, _ = get_noqa_suppressions(file_contents)
        self.assertTrue(whole_file)

    def test_ignore_lines(self):
        file_contents = self._get_file_contents('test_ignore_lines/test.py')
        _, lines = get_noqa_suppressions(file_contents)
        self.assertSetEqual(set((2, 3)), lines)