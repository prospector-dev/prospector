import os
import re
import warnings
from pathlib import Path
from typing import Union

from requirements_detector import find_requirements
from requirements_detector.detect import RequirementsNotFound

from prospector import encoding
from prospector.exceptions import PermissionMissing
from prospector.pathutils import is_virtualenv

POSSIBLE_LIBRARIES = ("django", "celery", "flask")


# see http://docs.python.org/2/reference/lexical_analysis.html#identifiers
_FROM_IMPORT_REGEX = re.compile(r"^\s*from ([\._a-zA-Z0-9]+) import .*$")
_IMPORT_REGEX = re.compile(r"^\s*import ([\._a-zA-Z0-9]+)$")
_IMPORT_MULTIPLE_REGEX = re.compile(r"^\s*import ([\._a-zA-Z0-9]+(, ){1})+")


def find_from_imports(file_contents: str) -> set[str]:
    names = set()
    for line in file_contents.split("\n"):
        match = _IMPORT_MULTIPLE_REGEX.match(line)
        if match:
            import_names = []
            first = match.group(1)
            import_names.append(first[:-2])
            for name in line.split(first)[1].split(","):
                import_names.append(name.strip())
        else:
            match = _IMPORT_REGEX.match(line) or _FROM_IMPORT_REGEX.match(line)
            if match is None:
                continue
            import_names = match.group(1).split(".")

        for import_name in import_names:
            if import_name in POSSIBLE_LIBRARIES:
                names.add(import_name)

    return names


def find_from_path(path: Path) -> set[str]:
    names = set()

    try:
        for item in path.iterdir():
            if item.is_dir():
                if is_virtualenv(item):
                    continue
                names |= find_from_path(item)
            elif not item.is_symlink() and item.suffix == ".py":
                try:
                    contents = encoding.read_py_file(item)
                    names |= find_from_imports(contents)
                except encoding.CouldNotHandleEncoding as err:
                    # TODO: this output will break output formats such as JSON
                    warnings.warn(f"{err.path}: {err.__cause__}", ImportWarning, stacklevel=0)

            if len(names) == len(POSSIBLE_LIBRARIES):
                # don't continue on recursing, there's no point!
                break
    except PermissionError as err:
        raise PermissionMissing(path) from err

    return names


def find_from_requirements(path: Union[str, Path]) -> set[str]:
    reqs = find_requirements(path)
    names: set[str] = set()
    for requirement in reqs:
        if requirement.name is not None and requirement.name.lower() in POSSIBLE_LIBRARIES:
            names.add(requirement.name.lower())
    return names


def autodetect_libraries(path: Union[str, Path]) -> set[str]:
    if os.path.isfile(path):
        path = os.path.dirname(path)
        if path == "":
            path = "."

    libraries: set[str] = set()

    try:
        libraries = find_from_requirements(path)
    except RequirementsNotFound:
        pass

    if len(libraries) < len(POSSIBLE_LIBRARIES):
        libraries = find_from_path(Path(path))

    return libraries
