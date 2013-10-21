import re
import sys
import os
from prospector.tools.base import ToolBase
from prospector.tools.pylint.collector import Collector
from prospector.tools.pylint.linter import ProspectorLinter


_IGNORE_PATHS = map(re.compile, (
    r'^setup.py$',
))


def _ignore_path(rootpath, path):
    if path.startswith(rootpath):
        path = path[len(rootpath):]
    return any([ignore.match(path) for ignore in _IGNORE_PATHS])


def _find_package_paths(rootpath):
    sys_path = set()
    check_dirs = []

    for subdir in os.listdir(rootpath):
        if subdir.startswith('.'):
            continue

        subdir_fullpath = os.path.join(rootpath, subdir)

        if os.path.islink(subdir_fullpath):
            continue

        if os.path.isfile(subdir_fullpath):
            if not subdir.endswith('.py'):         
                continue

            if os.path.exists(os.path.join(rootpath, '__init__.py')):
                continue

            # this is a python module but not in a package, so add it
            check_dirs.append(subdir_fullpath)
         
        elif os.path.exists(os.path.join(subdir_fullpath, '__init__.py')):
            # this is a package, add it and move on
            if not _ignore_path(rootpath, subdir_fullpath):
                sys_path.add(rootpath)
                check_dirs.append(subdir_fullpath)
        else:
            # this is not a package, so check its subdirs
            add_sys_path, add_check_dirs = _find_package_paths(subdir_fullpath)
            sys_path |= add_sys_path
            check_dirs += add_check_dirs
    return sys_path, check_dirs


class PylintTool(ToolBase):

    def __init__(self):
        self._args = self._extra_sys_path = self._collector = self._linter = None

    def prepare(self, rootpath, args, adaptors):
        linter = ProspectorLinter()
        linter.load_default_plugins()

        extra_sys_path, check_paths = _find_package_paths(rootpath)

        # insert the target path into the system path to get correct behaviour
        self._orig_sys_path = sys.path
        # note: we prepend, so that modules are preferentially found in the path
        # given as an argument. This prevents problems where we are checking a module
        # which is already on sys.path before this manipulation - for example, if we
        # are checking 'requests' in a local checkout, but 'requests' is already
        # installed system wide, pylint will discover the system-wide modules first
        # if the local checkout does not appear first in the path
        sys.path = list(extra_sys_path) + sys.path

        for adaptor in adaptors:
            adaptor.adapt_pylint(linter)

        self._args = linter.load_command_line_configuration(check_paths)

        # disable the warnings about disabling warnings...
        linter.disable('I0011')
        linter.disable('I0012')
        linter.disable('I0020')
        linter.disable('I0021')

        # use the collector 'reporter' to simply gather the messages given by PyLint
        self._collector = Collector()
        linter.set_reporter(self._collector)

        self._linter = linter

    def run(self):
        # note: Pylint will exit with a status code indicating the health of the
        # code it was checking. Prospector will not mimic this behaviour, as it
        # interferes with scripts which depend on and expect the exit code of the
        # code checker to match whether the check itself was successful
        self._linter.check(self._args)
        sys.path = self._orig_sys_path

        return self._collector.get_messages()
