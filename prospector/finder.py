from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Callable, Optional

from prospector.exceptions import PermissionMissing
from prospector.pathutils import is_python_module, is_python_package, is_virtualenv

_SKIP_DIRECTORIES = (".git", ".tox", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__", "node_modules")


class FileFinder:
    """
    This class is responsible for taking a combination of command-line arguments
    and configuration loaded from a profile to discover all files and modules which
    should be inspected.

    Individual tools can be told to ignore certain files, so the job of this class
    is basically to know which files to pass to which tools to be inspected.
    """

    def __init__(self, *provided_paths: Path, exclusion_filters: Optional[Iterable[Callable[[Path], bool]]] = None):
        """
        :param provided_paths:
            A list of Path objects to search for files and modules - can be either directories or files
        :param exclusion_filters:
            An optional list of filters. All paths will be checked against this list - if any return True,
            the path is excluded.
        """
        self._provided_files = []
        self._provided_dirs = []
        self._exclusion_filters = [
            # we always want to ignore some things
            lambda _path: _path.is_dir() and _path.name in _SKIP_DIRECTORIES,
            is_virtualenv,
        ] + list(exclusion_filters or [])

        for path in provided_paths:
            if not path.exists():
                raise FileNotFoundError(path)
            # ensure all paths from now one are absolute paths; they can be converted
            # to relative paths for output purposes later
            path = path.absolute()
            if path.is_file():
                self._provided_files.append(path)
            if path.is_dir():
                self._provided_dirs.append(path)

    def make_syspath(self) -> list[Path]:
        paths = set()
        for path in self._provided_dirs:
            paths.add(path)
        for module in self.python_modules:
            paths.add(module.parent)
        return sorted(paths)

    def is_excluded(self, path: Path) -> bool:
        return any(filt(path) for filt in self._exclusion_filters)

    def _filter(self, paths: Iterable[Path]) -> set[Path]:
        return {path for path in paths if not self.is_excluded(path)}

    def _walk(self, directory: Path) -> Iterator[Path]:
        if not self.is_excluded(directory):
            yield directory

        for path in directory.iterdir():
            if self.is_excluded(path):
                continue
            if path.is_dir():
                yield from self._walk(path)
            else:
                yield path

    @property
    def files(self) -> set[Path]:
        """
        List every individual file found from the given configuration.

        This method is useful for tools which require an explicit list of files to check.
        """
        files = set()

        for directory in self.directories:
            for path in self._walk(directory):
                if path.is_file():
                    files.add(path)

        files = self._filter(files)

        for path in self._provided_files:
            files.add(path)

        return files

    @property
    def python_packages(self) -> list[Path]:
        """
        Lists every directory found in the given configuration which is a python module (that is,
        contains an `__init__.py` file).

        This method is useful for passing to tools which will do their own discovery of python files.
        """
        return [d for d in self.directories if is_python_package(d)]

    @property
    def python_modules(self) -> list[Path]:
        """
        Lists every directory found in the given configuration which is a python module (that is,
        contains an `__init__.py` file).

        This method is useful for passing to tools which will do their own discovery of python files.
        """
        return [f for f in self.files if is_python_module(f)]

    @property
    def directories(self) -> set[Path]:
        """
        Lists every directory found from the given configuration, regardless of its contents.

        This method is useful for passing to tools which will do their own discovery of python files.
        """
        dirs = set()
        for directory in self._provided_dirs:
            dirs.add(directory)
            try:
                for obj in self._walk(directory):
                    if obj.is_dir():
                        dirs.add(obj)
            except PermissionError as err:
                raise PermissionMissing(obj) from err

        return self._filter(dirs)
