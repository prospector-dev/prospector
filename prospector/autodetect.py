import codecs
import warnings
import os
import re
from requirements_detector import find_requirements
from requirements_detector.detect import RequirementsNotFound


POSSIBLE_LIBRARIES = ('django', 'celery')


# see http://docs.python.org/2/reference/lexical_analysis.html#identifiers
_FROM_IMPORT_REGEX = re.compile(r'^\s*from ([\._a-zA-Z0-9]+) import .*$')
_IMPORT_REGEX = re.compile(r'^\s*import ([\._a-zA-Z0-9]+)$')
_IMPORT_MULTIPLE_REGEX = re.compile(r'^\s*import ([\._a-zA-Z0-9]+(, ){1})+')
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
            ('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE))):
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
            match = next(re.finditer(_CODING_REGEX, line.decode('ascii')), None)
            if match:
                return match.group(1)
        return default


def find_from_imports(file_contents):
    names = set()
    for line in file_contents.split('\n'):
        match = _IMPORT_MULTIPLE_REGEX.match(line)
        if match:
            import_names = []
            first = match.group(1)
            import_names.append(first[:-2])
            for name in line.split(first)[1].split(','):
                import_names.append(name.strip())
        else:
            match = _IMPORT_REGEX.match(line) or _FROM_IMPORT_REGEX.match(line)
            if match is None:
                continue
            import_names = match.group(1).split('.')

        for import_name in import_names:
            if import_name in POSSIBLE_LIBRARIES:
                names.add(import_name)

    return names


def find_from_path(path):
    names = set()
    max_possible = len(POSSIBLE_LIBRARIES)

    for item in os.listdir(path):
        item_path = os.path.abspath(os.path.join(path, item))
        if os.path.isdir(item_path):
            names |= find_from_path(item_path)
        elif not os.path.islink(item_path) and item_path.endswith('.py'):
            try:
                encoding = determine_pyfile_encoding(item_path, default='utf8')
                with codecs.open(item_path, encoding=encoding) as fip:
                    names |= find_from_imports(fip.read())
            except UnicodeDecodeError as err:
                # this warning is issued: (1) in determine_pyfile_encoding for
                # badly authored files (contains non-utf8 in a comment line), or
                # in find_from_imports() for either (2) a coding is specified,
                # but wrong and (3) no coding is specified, and the default
                # 'utf8' fails to decode.
                warnings.warn('{0}: {1}'.format(item_path, err), ImportWarning)
            except LookupError as err:
                # an invalid 'coding' statement specified in target source file
                warnings.warn('{0}: {1}'.format(item_path, err), ImportWarning)

        if len(names) == max_possible:
            # don't continue on recursing, there's no point!
            break

    return names


def find_from_requirements(path):
    reqs = find_requirements(path)
    names = []
    for requirement in reqs:
        if (requirement.name is not None
                and requirement.name.lower() in POSSIBLE_LIBRARIES):
            names.append(requirement.name.lower())
    return names


def autodetect_libraries(path):

    if os.path.isfile(path):
        path = os.path.dirname(path)
        if path == '':
            path = '.'

    libraries = []

    try:
        libraries = find_from_requirements(path)

    # pylint: disable=pointless-except
    except RequirementsNotFound:
        pass

    if len(libraries) < len(POSSIBLE_LIBRARIES):
        libraries = find_from_path(path)

    return libraries
