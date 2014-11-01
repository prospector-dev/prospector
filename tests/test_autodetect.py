from unittest import TestCase
from prospector.autodetect import find_from_imports


class FindFromImportsTest(TestCase):

    def _test(self, contents, *expected_names):
        names = find_from_imports(contents)
        self.assertEqual(set(expected_names), names)

    def test_simple_imports(self):
        self._test('from django.db import models', 'django')
        self._test('import django', 'django')
        self._test('from django import db\nfrom celery import task', 'django', 'celery')

    def test_multiple_imports(self):
        self._test('from django.db import (models, \n'
                   '    some, other, stuff)', 'django')

    def test_indented_imports(self):
        self._test('def lala(self):\n    from django.db import models\n    return models.Model', 'django')
     
    def test_same_line_two_imports(self):
        self._test('import django, celery', 'django', 'celery')

if __name__ == '__main__':
    import unittest
    unittest.main()
