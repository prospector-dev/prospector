# -*- coding: utf-8 -*-
import sys
import tokenize


class CouldNotHandleEncoding(Exception):
    def __init__(self, path, cause):
        self.path = path
        self.cause = cause


def read_py_file(filepath):
    if sys.version_info < (3, ):
        return open(filepath, 'rU').read()
    else:
        # see https://docs.python.org/3/library/tokenize.html#tokenize.detect_encoding
        # first just see if the file is properly encoded
        try:
            with open(filepath, 'rb') as f:
                tokenize.detect_encoding(f.readline)
        except SyntaxError as err:
            # this warning is issued:
            #   (1) in badly authored files (contains non-utf8 in a comment line)
            #   (2) a coding is specified, but wrong and
            #   (3) no coding is specified, and the default
            #       'utf8' fails to decode.
            #   (4) the encoding specified by a pep263 declaration did not match
            #       with the encoding detected by inspecting the BOM
            raise CouldNotHandleEncoding(filepath, err)

        try:
            return tokenize.open(filepath).read()
            # this warning is issued:
            #   (1) if uft-8 is specified, but latin1 is used with something like \x0e9 appearing
            #       (see http://stackoverflow.com/a/5552623)
        except UnicodeDecodeError as err:
            raise CouldNotHandleEncoding(filepath, err)
