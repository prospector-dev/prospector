# -*- coding: utf-8 -*-
import os

from prospector.pathutils import is_virtualenv


class SingleFiles(object):

    """
    When prospector is run in 'single file mode' - that is,
    the argument is a python module rather than a directory -
    then we'll use this object instead of the FoundFiles to
    give all the functionality needed to check a single file.
    """

    # The 'even if ignored' parameters are kept to show this is meant
    # to be API compatible with FoundFiles, but pylint will warn, so
    # let's disable
    # pylint:disable=unused-argument
    def __init__(self, files, rootpath):
        self.files = files
        self.rootpath = rootpath

    def _check(self, checkpath, abspath=True):
        if abspath:
            checkpath = os.path.abspath(checkpath)
            return checkpath in map(os.path.abspath, self.files)
        return checkpath in self.files

    def check_module(self, filepath, abspath=True, even_if_ignored=False):
        return self._check(filepath, abspath)

    def check_package(self, filepath, abspath=True, even_if_ignored=False):
        return self._check(filepath, abspath)

    def check_file(self, filepath, abspath=True, even_if_ignored=False):
        return self._check(filepath, abspath)

    def iter_file_paths(self, abspath=True, include_ignored=False):
        for filepath in self.files:
            yield os.path.abspath(filepath) if abspath else filepath

    def iter_package_paths(self, abspath=True, include_ignored=False):
        for filepath in self.files:
            yield os.path.abspath(filepath) if abspath else filepath

    def iter_directory_paths(self, abspath=True, include_ignored=False):
        for filepath in self.files:
            filepath = os.path.dirname(filepath)
            yield os.path.abspath(filepath) if abspath else filepath

    def iter_module_paths(self, abspath=True, include_ignored=False):
        for filepath in self.files:
            yield os.path.abspath(filepath) if abspath else filepath

    def to_absolute_path(self, path):
        return os.path.abspath(os.path.join(self.rootpath, path))

    def get_minimal_syspath(self, absolute_paths=True):
        paths = list(set(map(os.path.dirname, self.files)))
        if absolute_paths:
            paths = list(map(os.path.abspath, paths))
        return [self.rootpath] + paths


class FoundFiles(object):
    def __init__(self, rootpath, files, modules, packages, directories, ignores):
        self.rootpath = rootpath
        self._files = files
        self._modules = modules
        self._packages = packages
        self._directories = directories
        self._ignores = ignores

    def _check(self, filepath, pathlist, abspath=True, even_if_ignored=False):
        path = os.path.relpath(filepath, self.rootpath) if abspath else filepath
        for checkpath, ignored in pathlist:
            if path == checkpath:
                if ignored and not even_if_ignored:
                    break
                return True
        return False

    def check_module(self, filepath, abspath=True, even_if_ignored=False):
        return self._check(filepath, self._modules, abspath, even_if_ignored)

    def check_package(self, filepath, abspath=True, even_if_ignored=False):
        return self._check(filepath, self._packages, abspath, even_if_ignored)

    def check_file(self, filepath, abspath=True, even_if_ignored=False):
        return self._check(filepath, self._files, abspath, even_if_ignored)

    def _iter_paths(self, pathlist, abspath=True, include_ignored=False):
        for path, ignored in pathlist:
            if ignored and not include_ignored:
                continue
            if abspath:
                path = self.to_absolute_path(path)
            yield path

    def iter_file_paths(self, abspath=True, include_ignored=False):
        return self._iter_paths(self._files, abspath, include_ignored)

    def iter_package_paths(self, abspath=True, include_ignored=False):
        return self._iter_paths(self._packages, abspath, include_ignored)

    def iter_directory_paths(self, abspath=True, include_ignored=False):
        return self._iter_paths(self._directories, abspath, include_ignored)

    def iter_module_paths(self, abspath=True, include_ignored=False):
        return self._iter_paths(self._modules, abspath, include_ignored)

    def to_absolute_path(self, path):
        return os.path.abspath(os.path.join(self.rootpath, path))

    def get_minimal_syspath(self, absolute_paths=True):
        """
        Provide a list of directories that, when added to sys.path, would enable
        any of the discovered python modules to be found
        """
        # firstly, gather a list of the minimum path to each package
        package_list = set()
        packages = [p[0] for p in self._packages if not p[1]]
        for package in sorted(packages, key=len):
            parent = os.path.split(package)[0]
            if parent not in packages and parent not in package_list:
                package_list.add(parent)

        # now add the directory containing any modules who are not in packages
        module_list = []
        modules = [m[0] for m in self._modules if not m[1]]
        for module in modules:
            dirname = os.path.dirname(module)
            if dirname not in packages:
                module_list.append(dirname)

        full_list = sorted(set(module_list) | package_list, key=len)
        if absolute_paths:
            full_list = [os.path.join(self.rootpath, p).rstrip(os.path.sep) for p in full_list]
        return full_list


def _find_paths(ignore, curpath, rootpath):
    files, modules, packages, directories = [], [], [], []

    for filename in os.listdir(curpath):
        fullpath = os.path.join(curpath, filename)
        try:
            relpath = os.path.relpath(fullpath, rootpath)
        except ValueError:
            # relpath breaks on long paths in Windows
            continue

        if filename.startswith('.') and os.path.isdir(fullpath):
            continue

        if os.path.islink(fullpath):
            continue

        ignored = any([m.search(relpath) for m in ignore])

        if os.path.isdir(fullpath):

            # is it probably a virtualenvironment?
            if is_virtualenv(fullpath) or '.tox' in fullpath:
                continue

            # this is a directory
            directories.append((relpath, ignored))

            # is it also a package?
            initpy = os.path.join(fullpath, '__init__.py')
            if os.path.exists(initpy) and os.path.isfile(initpy):
                packages.append((relpath, ignored))

            # do the same for this directory
            recurse = _find_paths(ignore, os.path.join(curpath, filename), rootpath)
            files += recurse[0]
            modules += recurse[1]
            packages += recurse[2]
            directories += recurse[3]

        else:
            # this is a file, is it a python module?
            if fullpath.endswith('.py'):
                modules.append((relpath, ignored))
            files.append((relpath, ignored))

    return files, modules, packages, directories


def find_python(ignores, paths, explicit_file_mode, workdir=''):
    """
    Returns a FoundFiles class containing a list of files, packages, directories,
    where files are simply all python (.py) files, packages are directories
    containing an `__init__.py` file, and directories is a list of all directories.
    All paths are relative to the dirpath argument.
    """
    if explicit_file_mode:
        return SingleFiles(paths, workdir or os.getcwd())
    else:
        assert len(paths) == 1
        files, modules, directories, packages = _find_paths(ignores, paths[0], workdir)
        return FoundFiles(workdir, files, modules, directories, packages, ignores)
