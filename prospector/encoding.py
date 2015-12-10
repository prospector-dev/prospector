# -*- coding: utf-8 -*-
import codecs
import re


class CouldNotHandleEncoding(Exception):
    def __init__(self, path, cause):
        self.path = path
        self.cause = cause


_CODING_REGEX = re.compile(r'coding[:=]\s*([-\w.]+)')


def detect_by_bom(path):
    """
    Determine and return file encoding using BOM character.

    This is necessary for files such as setuptools' tests/script-with-bom.py

    :returns bom-detected encoding only if discovered
    """
    with open(path, 'rb') as fin:
        raw = fin.read(4)
    for enc, boms in (
        ('utf-8-sig', (codecs.BOM_UTF8,)),
        ('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),
        ('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE))
    ):
        if any(raw.startswith(bom) for bom in boms):
            return enc


def determine_pyfile_encoding(path, default='utf8'):
    """
    Determine and return file encoding of a python source file.

    https://www.python.org/dev/peps/pep-0263/

    :returns: file encoding if determined, otherwise ``default``.
    """
    encoding = detect_by_bom(path)
    if encoding:
        # trust the byte-order mark
        return encoding

    with open(path, 'rb') as fip:
        # look for string of form '# coding: <encoding>'
        # in the first two lines of python source file.
        for line in (_line for _line in
                     (fip.readline(), fip.readline())
                     if _line.decode(default).startswith('#')):
            match = re.search(_CODING_REGEX, line.decode(default))
            if match:
                return match.group(1)
        return default


def read_py_file(path):
    encoding = determine_pyfile_encoding(path, default='utf8')
    with codecs.open(path, encoding=encoding) as fip:
        try:
            return fip.read()
        except UnicodeDecodeError as err:
            # this warning is issued: (1) in determine_pyfile_encoding for
            # badly authored files (contains non-utf8 in a comment line), or
            # in find_from_imports() for either (2) a coding is specified,
            # but wrong and (3) no coding is specified, and the default
            # 'utf8' fails to decode.
            raise CouldNotHandleEncoding(path, err)
        except LookupError as err:
            # an invalid 'coding' statement specified in target source file
            raise CouldNotHandleEncoding(path, err)
