from collections import defaultdict
import re
import sys
import os
from prospector.message import Message
from prospector.tools.base import ToolBase
from prospector.tools.pylint.collector import Collector
from prospector.tools.pylint.indent_checker import IndentChecker
from prospector.tools.pylint.linter import ProspectorLinter


_W0614_RE = re.compile(r'^Unused import (.*) from wildcard import$')


def _find_package_paths(ignore, rootpath):
    sys_path = set()
    check_dirs = []

    for subdir in os.listdir(rootpath):
        if subdir.startswith('.'):
            continue

        subdir_fullpath = os.path.join(rootpath, subdir)
        rel_path = os.path.relpath(subdir_fullpath, rootpath)

        if os.path.islink(subdir_fullpath):
            continue

        if os.path.isfile(subdir_fullpath):
            if not subdir.endswith('.py'):
                continue

            if os.path.exists(os.path.join(rootpath, '__init__.py')):
                continue

            # this is a python module but not in a package, so add it
            if any([m.search(rel_path) for m in ignore]):
                continue
            check_dirs.append(subdir_fullpath)

        elif os.path.exists(os.path.join(subdir_fullpath, '__init__.py')):
            # this is a package, add it and move on
            if any([m.search(rel_path) for m in ignore]):
                continue
            sys_path.add(rootpath)
            check_dirs.append(subdir_fullpath)
        else:
            # this is not a package, so check its subdirs
            add_sys_path, add_check_dirs = _find_package_paths(
                ignore,
                subdir_fullpath,
            )
            sys_path |= add_sys_path
            check_dirs += add_check_dirs
    return sys_path, check_dirs


class PylintTool(ToolBase):

    def __init__(self):
        self._args = self._extra_sys_path = None
        self._collector = self._linter = None
        self._orig_sys_path = []

    def prepare(self, rootpath, ignore, args, adaptors):
        linter = ProspectorLinter(ignore, rootpath)
        linter.load_default_plugins()

        extra_sys_path, check_paths = _find_package_paths(ignore, rootpath)

        # insert the target path into the system path to get correct behaviour
        self._orig_sys_path = sys.path
        # note: we prepend, so that modules are preferentially found in the
        # path given as an argument. This prevents problems where we are
        # checking a module which is already on sys.path before this
        # manipulation - for example, if we are checking 'requests' in a local
        # checkout, but 'requests' is already installed system wide, pylint
        # will discover the system-wide modules first if the local checkout
        # does not appear first in the path
        sys.path = list(extra_sys_path) + sys.path

        for adaptor in adaptors:
            adaptor.adapt_pylint(linter)

        self._args = linter.load_command_line_configuration(check_paths)

        # disable the warnings about disabling warnings...
        linter.disable('I0011')
        linter.disable('I0012')
        linter.disable('I0020')
        linter.disable('I0021')

        # disable the 'mixed indentation' warning, since it actually will only allow
        # the indentation specified in the pylint configuration file; we replace it
        # instead with our own version which is more lenient and configurable
        linter.disable('W0312')
        indent_checker = IndentChecker(linter)
        linter.register_checker(indent_checker)

        # we don't want similarity reports right now
        linter.disable('similarities')

        # use the collector 'reporter' to simply gather the messages
        # given by PyLint
        self._collector = Collector()
        linter.set_reporter(self._collector)

        for checker in linter.get_checkers():
            if not hasattr(checker, 'options'):
                continue
            for option in checker.options:
                if args.max_line_length is not None:
                    if option[0] == 'max-line-length':
                        checker.set_option('max-line-length', args.max_line_length)

        self._linter = linter

    def _combine_w0614(self, messages):
        """
        For the "unused import from wildcard import" messages, we want to combine all warnings about
        the same line into a single message
        """
        by_loc = defaultdict(list)
        out = []

        for message in messages:
            if message.code == 'W0614':
                by_loc[message.location].append(message)
            else:
                out.append(message)

        for location, message_list in by_loc.items():
            names = []
            for msg in message_list:
                names.append(_W0614_RE.match(msg.message).group(1))

            msgtxt = 'Unused imports from wildcard import: %s' % ', '.join(names)
            combined_message = Message('pylint', 'W0614', location, msgtxt)
            out.append(combined_message)

        return out

    def _combine_(self, messages):
        pass

    def combine(self, messages):
        """
        Some error messages are repeated, causing many errors where only one is strictly necessary. For
        example, having a wildcard import will result in one 'Unused Import' warning for every unused import.
        This method will combine these into a single warning.
        """
        combined = self._combine_w0614(messages)
        return sorted(combined)

    def run(self):
        # note: Pylint will exit with a status code indicating the health of
        # the code it was checking. Prospector will not mimic this behaviour,
        # as it interferes with scripts which depend on and expect the exit
        # code of the code checker to match whether the check itself was
        # successful
        self._linter.check(self._args)
        sys.path = self._orig_sys_path

        messages = self._collector.get_messages()
        return self.combine(messages)
