# -*- coding: utf-8 -*-
import sys
import tokenize


def read_py_file(filename):
    if sys.version_info < (3, ):
        return open(filename, 'rU').read()
    else:
        return tokenize.open(filename).read()
