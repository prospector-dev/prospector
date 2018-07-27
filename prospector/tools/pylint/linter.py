from __future__ import absolute_import

from pylint.__pkginfo__ import numversion as PYLINT_VERSION
if PYLINT_VERSION >= (1, 5):
    from pylint.config import OptionsManagerMixIn
    from pylint.utils import _splitstrip
else:
    from logilab.common.configuration import OptionsManagerMixIn
from pylint.lint import PyLinter


class ProspectorLinter(PyLinter):  # pylint: disable=too-many-ancestors,too-many-public-methods

    def __init__(self, found_files, *args, **kwargs):
        self._files = found_files

        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

    def config_from_file(self, config_file=None):
        """Will return `True` if plugins have been loaded. For pylint>=1.5. Else `False`."""
        if PYLINT_VERSION >= (1, 5):
            if PYLINT_VERSION >= (2, 0):
                self.read_config_file(config_file)
            else:
                self.read_config_file(config_file, quiet=True)
            if self.cfgfile_parser.has_option('MASTER', 'load-plugins'):
                # pylint: disable=protected-access
                plugins = _splitstrip(self.cfgfile_parser.get('MASTER', 'load-plugins'))
                self.load_plugin_modules(plugins)
            self.load_config_file()
            return True

        self.load_file_configuration(config_file)
        return False

    def reset_options(self):
        # for example, we want to re-initialise the OptionsManagerMixin
        # to supress the config error warning
        # pylint: disable=non-parent-init-called
        if PYLINT_VERSION >= (2, 0):
            OptionsManagerMixIn.__init__(self, usage=PyLinter.__doc__)
        else:
            OptionsManagerMixIn.__init__(self, usage=PyLinter.__doc__, quiet=True)

    def expand_files(self, modules):
        expanded = PyLinter.expand_files(self, modules)
        filtered = []
        for module in expanded:
            if self._files.check_module(module['path']):
                filtered.append(module)
        return filtered
