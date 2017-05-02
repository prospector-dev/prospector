from __future__ import absolute_import
from prospector.encoding import read_py_file
import os
from unittest import TestCase


class InvalidUTF8Byte(TestCase):

    def test_invalid_utf8_byte(self):
        filepath = os.path.join(os.path.dirname(__file__), 'testdata/invalid-utf8-byte.py')
        lines = read_py_file(filepath)