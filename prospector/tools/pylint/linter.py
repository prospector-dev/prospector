from pathlib import Path

from pylint.lint import PyLinter
from pylint.utils import _splitstrip


class ProspectorLinter(PyLinter):
    def __init__(self, found_files, *args, **kwargs):
        self._files = found_files
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

    def config_from_file(self, config_file=None):
        """Will return `True` if plugins have been loaded. For pylint>=1.5. Else `False`."""
        self.read_config_file(config_file)
        if self.cfgfile_parser.has_option("MASTER", "load-plugins"):
            plugins = _splitstrip(self.cfgfile_parser.get("MASTER", "load-plugins"))
            self.load_plugin_modules(plugins)
        self.load_config_file()
        return True

    def _expand_files(self, modules):
        expanded = super()._expand_files(modules)
        filtered = {}
        for module in expanded:
            # need to de-duplicate, as pylint also walks directories given to it, so it will find
            # files that prospector has already provided and end up checking it more than once
            if not self._files.is_excluded(Path(module["path"])):
                # if the key exists, just overwrite it with the same value, so we don't need an extra if statement
                filtered[module["path"]] = module
        return filtered.values()
