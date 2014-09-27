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
        # firstly, gather a list of the minimum path to each package
        package_list = set()
        for package in sorted(self.packages, key=lambda x: len(x)):
            parent = os.path.split(package)[0]
            if parent not in self.packages and parent not in package_list:
                package_list.add(parent)

        # now add the directory containing any modules who are not in packages
        module_list = []
        for module in self.modules:
            dirname = os.path.dirname(module)
            if dirname not in self.packages:
                module_list.append(dirname)

        full_list = sorted(set(module_list) | package_list, key=lambda x: len(x))
        full_list = [os.path.join(self.rootpath, p).rstrip(os.path.sep) for p in full_list]
        return full_list


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
