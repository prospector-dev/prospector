from functools import cached_property
from pathlib import Path
from typing import Callable, Iterable, Iterator, List

from prospector.pathutils import is_python_module, is_python_package, is_virtualenv

_SKIP_DIRECTORIES = (".git", ".tox", ".mypy_cache", ".pytest_cache", ".venv", "dist", "__pycache__")


class FileFinder:
    """
    This class is responsible for taking a combination of command-line arguments
    and configuration loaded from a profile to discover all files and modules which
    should be inspected.

    Individual tools can be told to ignore certain files, so the job of this class
    is basically to know which files to pass to which tools to be inspected.
    """

    def __init__(self, *provided_paths: Path, workdir: Path = None, exclusion_filters: Iterable[Callable] = None):
        """
        :param provided_paths:
            A list of Path objects to search for files and modules - can be either directories or files
        :param exclusion_filters:
            An optional list of filters. All paths will be checked against this list - if any return True,
            the path is excluded.
        """
        self.workdir = workdir or Path.cwd()
        self._provided_files = []
        self._provided_dirs = []
        self._exclusion_filters = exclusion_filters or []

        if exclusion_filters is not None:
            self._exclusion_filters += exclusion_filters

        for path in provided_paths:
            if not path.exists():
                raise FileNotFoundError(path)
            if path.is_file():
                self._provided_files.append(path)
            if path.is_dir():
                self._provided_dirs.append(path)

    def is_excluded(self, path: Path) -> bool:
        # we always want to ignore some things
        filters = [
            lambda path: path.is_dir() and path.name in _SKIP_DIRECTORIES,
            lambda path: is_virtualenv(path),
        ] + self._exclusion_filters

        for filt in filters:
            if filt(path):
                return True
        return False

    def _filter(self, paths: Iterable[Path]) -> List[Path]:
        return [path for path in paths if not self.is_excluded(path)]

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

    #
    # def make_syspath(self) -> List[Path]:
    #     """
    #     Given the files that have been discovered, create a syspath which will allow all modules
    #     found to be imported.
    #
    #     :return: A list of directories or files to ensure are included in the system path
    #     """
    #     directories = set()
    #     for module in self.modules:
    #         directories.add(module.parent)
    #     return list[directories]

    @cached_property
    def files(self) -> List[Path]:
        """
        List every individual file found from the given configuration.

        This method is useful for tools which require an explicit list of files to check.
        """
        files = set()
        for path in self._provided_files:
            files.add(path)

        for directory in self.directories:
            for path in self._walk(directory):
                if path.is_file():
                    files.add(path)

        return self._filter(files)

    @cached_property
    def python_packages(self) -> List[Path]:
        """
        Lists every directory found in the given configuration which is a python module (that is,
        contains an `__init__.py` file).

        This method is useful for passing to tools which will do their own discovery of python files.
        """
        return self._filter(d for d in self.directories if is_python_package(d))

    @cached_property
    def python_modules(self) -> List[Path]:
        """
        Lists every directory found in the given configuration which is a python module (that is,
        contains an `__init__.py` file).

        This method is useful for passing to tools which will do their own discovery of python files.
        """
        return self._filter(f for f in self.files if is_python_module(f))

    @cached_property
    def directories(self) -> List[Path]:
        """
        Lists every directory found from the given configuration, regardless of its contents.

        This method is useful for passing to tools which will do their own discovery of python files.
        """
        dirs = set()
        for directory in self._provided_dirs:
            for obj in self._walk(directory):
                if obj.is_dir():
                    dirs.add(obj)

        return self._filter(dirs)
