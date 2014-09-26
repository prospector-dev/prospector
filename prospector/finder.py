import os


class FoundFiles(object):
    def __init__(self, rootpath, files, modules, packages, directories):
        self.rootpath = rootpath
        self.files = files
        self.modules = modules
        self.packages = packages
        self.directories = directories

    def check_module(self, filepath, abspath=True):
        path = os.path.relpath(filepath, self.rootpath) if abspath else filepath
        return path in self.modules

    def check_package(self, filepath, abspath=True):
        path = os.path.relpath(filepath, self.rootpath) if abspath else filepath
        return path in self.packages

    def check_file(self, filepath, abspath=True):
        path = os.path.relpath(filepath, self.rootpath) if abspath else filepath
        return path in self.files

    def iter_file_paths(self):
        for filepath in self.files:
            yield(os.path.abspath(os.path.join(self.rootpath, filepath)))

    def iter_package_paths(self):
        for package in self.packages:
            yield(os.path.abspath(os.path.join(self.rootpath, package)))

    def iter_directory_paths(self):
        for directory in self.directories:
            yield(os.path.abspath(os.path.join(self.rootpath, directory)))

    def iter_module_paths(self):
        for module in self.modules:
            yield(os.path.abspath(os.path.join(self.rootpath, module)))

    def get_minimal_syspath(self):
        """
        Provide a list of directories that, when added to sys.path, would enable
        any of the discovered python modules to be found
        """
        # for each package, we want the first directory which is a package
        # ie, a/b/c/__init.py will be also found by adding a/ to the syspath if a and a/b are also packages
        syspath = set()
        # sorting into order will mean that 'higher' packages are in the set by the time we look at 'lower' packages
        packages = sorted(self.packages, key=lambda x: len(x))
        for package in packages:
            dirs = package.split(os.path.sep)
            if len(dirs) <= 1:
                syspath.add(package)
                continue
            for i in range(1, len(dirs)):
                testpath = os.path.join(*dirs[:i])
                if testpath in syspath:
                    break
            else:
                syspath.add(package)

        # we also need to add directories containing any of the python modules discovered that are not
        # in a package
        for module in self.modules:
            module_dir = os.path.dirname(module)
            dirs = module_dir.split(os.path.sep)
            if len(dirs) <= 1:
                syspath.add(module_dir)
                continue
            for i in range(1, len(dirs)):
                testpath = os.path.join(*dirs[:i])
                if testpath in syspath:
                    break
            else:
                syspath.add(module_dir)

        return [os.path.join(self.rootpath, p) for p in syspath]


def _find_paths(ignore, curpath, rootpath):
    files, modules, packages, directories = [], [], [], []

    for filename in os.listdir(curpath):
        if filename.startswith('.'):
            continue

        fullpath = os.path.join(curpath, filename)
        relpath = os.path.relpath(fullpath, rootpath)

        if any([m.search(relpath) for m in ignore]):
            continue

        if os.path.islink(fullpath):
            continue

        if os.path.isdir(fullpath):
            # this is a directory, is it also a package?
            directories.append(relpath)
            initpy = os.path.join(fullpath, '__init__.py')
            if os.path.exists(initpy) and os.path.isfile(initpy):
                packages.append(relpath)

            # do the same for this directory
            recurse = _find_paths(ignore, os.path.join(curpath, filename), rootpath)
            files += recurse[0]
            modules += recurse[1]
            packages += recurse[2]
            directories += recurse[3]

        else:
            # this is a file, is it a python module?
            if fullpath.endswith('.py'):
                modules.append(relpath)
            files.append(relpath)

    return files, modules, packages, directories


def find_python(ignores, dirpath):
    """
    Returns a FoundFiles class containing a list of files, packages, directories,
    where files are simply all python (.py) files, packages are directories
    containing an `__init__.py` file, and directories is a list of all directories.
    All paths are relative to the dirpath argument.
    """
    files, modules, directories, packages = _find_paths(ignores, dirpath, dirpath)
    return FoundFiles(dirpath, files, modules, directories, packages)
