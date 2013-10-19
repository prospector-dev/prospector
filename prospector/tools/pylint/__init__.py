import re
import sys
import os
from prospector.tools.base import ToolBase
from prospector.tools.pylint.collector import Collector
from prospector.tools.pylint.linter import ProspectorLinter


_IGNORE_PATHS = map(re.compile, (
    r'^setup.py$',
))


class PylintTool(ToolBase):

    def __init__(self):
        self._args = self._extra_sys_path = self._collector = self._linter = None

    def _ignore_path(self, rootpath, path):
        print path
        return any([ignore.match(path) for ignore in _IGNORE_PATHS])

    def _find_paths(self, rootpath):
        # first find all packages in the root directory
        paths = self._find_packages(rootpath)
        # then add all python files in the root directory
        init_file = os.path.join(rootpath, '__init__.py')
        if os.path.exists(init_file) and os.path.isfile(init_file):
            paths.append(rootpath)
        else:
            for entry in os.listdir(rootpath):
                entry_path = os.path.join(rootpath, entry)
                if self._ignore_path(rootpath, entry_path):
                    continue
                if entry.endswith('.py') and os.path.isfile(entry_path):
                    paths.append(entry_path)
        return paths

    def _find_packages(self, rootpath):
        check_dirs = []

        for subdir in os.listdir(rootpath):
            subdir_fullpath = os.path.join(rootpath, subdir)

            if not os.path.isdir(subdir_fullpath):
                continue

            if os.path.exists(os.path.join(subdir_fullpath, '__init__.py')):
                # this is a package, add it and move on
                if not self._ignore_path(subdir_fullpath):
                    check_dirs.append(subdir_fullpath)
            else:
                # this is not a package, so check its subdirs
                check_dirs.extend(self._find_packages(subdir_fullpath))
        return check_dirs

    def prepare(self, rootpath, args, profiles):
        linter = ProspectorLinter()
        linter.load_default_plugins()

        paths = self._find_paths(rootpath)

        for profile in profiles:
            profile.apply_to_pylint(linter)

        self._args = linter.load_command_line_configuration(paths)

        # disable the warnings about disabling warnings...
        linter.disable('I0011')
        linter.disable('I0012')
        linter.disable('I0020')
        linter.disable('I0021')

        # insert the target path into the system path to get correct behaviour
        self._extra_sys_path = [rootpath]
        for path in paths:
            if os.path.isdir(path):
                self._extra_sys_path.append(path)
        sys.path += self._extra_sys_path

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
        for path in self._extra_sys_path:
            sys.path.remove(path)

        return self._collector.get_messages()
