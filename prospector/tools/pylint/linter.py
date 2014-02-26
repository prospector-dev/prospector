from __future__ import absolute_import
import os

from logilab.common.configuration import OptionsManagerMixIn
from pylint.lint import PyLinter


class ProspectorLinter(PyLinter):  # pylint: disable=R0901,R0904

    def __init__(self, ignore, rootpath, *args, **kwargs):
        self._ignore = ignore
        self._rootpath = rootpath

        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

        # do some additional things!

        # for example, we want to re-initialise the OptionsManagerMixin
        # to supress the config error warning
        # pylint: disable=W0233
        OptionsManagerMixIn.__init__(self, usage=PyLinter.__doc__, quiet=True)

    def expand_files(self, modules):
        expanded = PyLinter.expand_files(self, modules)
        filtered = []
        for module in expanded:
            rel_path = os.path.relpath(module['path'], self._rootpath)
            if any([m.search(rel_path) for m in self._ignore]):
                continue
            filtered.append(module)
        return filtered
