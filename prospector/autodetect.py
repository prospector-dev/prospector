import os
import re
from prospector.adaptor import LIBRARY_ADAPTORS
from requirements_detector import find_requirements
from requirements_detector.detect import RequirementsNotFound


# see http://docs.python.org/2/reference/lexical_analysis.html#identifiers
_FROM_IMPORT_REGEX = re.compile(r'^\s*from ([\._a-zA-Z0-9]+) import .*$')
_IMPORT_REGEX = re.compile(r'^\s*import ([\._a-zA-Z0-9]+)$')


def find_from_imports(file_contents):
    names = set()
    for line in file_contents.split('\n'):
        match = _IMPORT_REGEX.match(line)
        if match is None:
            match = _FROM_IMPORT_REGEX.match(line)
        if match is None:
            continue
        import_names = match.group(1).split('.')
        for import_name in import_names:
            if import_name in LIBRARY_ADAPTORS:
                names.add(import_name)
    return names


def find_from_path(path):
    names = set()
    max_possible = len(LIBRARY_ADAPTORS.keys())

    for item in os.listdir(path):
        item_path = os.path.abspath(os.path.join(path, item))
        if os.path.isdir(item_path):
            names |= find_from_path(item_path)
        elif not os.path.islink(item_path) and item_path.endswith('.py'):
            with open(item_path) as fip:
                names |= find_from_imports(fip.read())

        if len(names) == max_possible:
            # don't continue on recursing, there's no point!
            break

    return names


def find_from_requirements(path):
    reqs = find_requirements(path)
    names = []
    for requirement in reqs:
        if requirement.name is not None \
                and requirement.name.lower() in LIBRARY_ADAPTORS:
            names.append(requirement.name.lower())
    return names


def autodetect_libraries(path):

    adaptor_names = []

    try:
        adaptor_names = find_from_requirements(path)

    # pylint: disable=W0704
    except RequirementsNotFound:
        pass

    if len(adaptor_names) == 0:
        adaptor_names = find_from_path(path)

    adaptors = []
    for adaptor_name in adaptor_names:
        adaptors.append((adaptor_name, LIBRARY_ADAPTORS[adaptor_name]()))

    return adaptors
