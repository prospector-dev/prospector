import warnings
import os
import re
from requirements_detector import find_requirements
from requirements_detector.detect import RequirementsNotFound
from prospector import encoding
from prospector.pathutils import is_virtualenv


POSSIBLE_LIBRARIES = ('django', 'celery', 'flask')


# see http://docs.python.org/2/reference/lexical_analysis.html#identifiers
_FROM_IMPORT_REGEX = re.compile(r'^\s*from ([\._a-zA-Z0-9]+) import .*$')
_IMPORT_REGEX = re.compile(r'^\s*import ([\._a-zA-Z0-9]+)$')
_IMPORT_MULTIPLE_REGEX = re.compile(r'^\s*import ([\._a-zA-Z0-9]+(, ){1})+')


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
            if is_virtualenv(item_path):
                continue
            names |= find_from_path(item_path)
        elif not os.path.islink(item_path) and item_path.endswith('.py'):
            try:
                contents = encoding.read_py_file(item_path)
                names |= find_from_imports(contents)
            except encoding.CouldNotHandleEncoding as err:
                # TODO: this output will break output formats such as JSON
                warnings.warn('{0}: {1}'.format(err.path, err.cause), ImportWarning)

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
