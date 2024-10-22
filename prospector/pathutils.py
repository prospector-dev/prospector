import os
from pathlib import Path


def is_python_package(path: Path) -> bool:
    return path.is_dir() and (path / "__init__.py").exists()


def is_python_module(path: Path) -> bool:
    # TODO: is this too simple?
    return path.suffix == ".py"


def is_virtualenv(path: Path) -> bool:
    clues = ("Scripts", "lib", "include") if os.name == "nt" else ("bin", "lib", "include")

    try:
        # just get the name, iterdir returns absolute paths by default
        dircontents = [obj.name for obj in path.iterdir()]
    except (OSError, TypeError):
        # listdir failed, probably due to path length issues in windows
        return False

    if not all(clue in dircontents for clue in clues):
        # we don't have the 3 directories which would imply
        # this is a virtualenvironment
        return False

    if not all((path / clue).is_dir() for clue in clues):
        # some of them are not actually directories
        return False

    # if we do have all three directories, make sure that it's not
    # just a coincidence by doing some heuristics on the rest of
    # the directory
    # if there are more than 7 things it's probably not a virtualenvironment
    return len(dircontents) <= 7
