from pathlib import Path

from packaging import version as packaging_version
from pylint import version as pylint_version
from pylint.config.config_file_parser import _ConfigurationFileParser
from pylint.config.config_initialization import _order_all_first
from pylint.lint import PyLinter
from pylint.utils import _splitstrip, utils


class ProspectorLinter(PyLinter):
    def __init__(self, found_files, *args, **kwargs):
        self._files = found_files
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

    # Largely inspired by https://github.com/pylint-dev/pylint/blob/main/pylint/config/config_initialization.py#L26
    def config_from_file(self, config_file=None):
        """Will return `True` if plugins have been loaded. For pylint>=1.5. Else `False`."""
        config_file_parser = _ConfigurationFileParser(False, self)
        config_data, config_args = config_file_parser.parse_config_file(file_path=config_file)
        if config_data.get("MASTER", {}).get("load-plugins"):
            plugins = _splitstrip(config_data["MASTER"]["load-plugins"])
            self.load_plugin_modules(plugins)

        config_args = _order_all_first(config_args, joined=False)

        if "init-hook" in config_data:
            exec(utils._unquote(config_data["init-hook"]))  # pylint: disable=exec-used

        # Load plugins if specified in the config file
        if "load-plugins" in config_data:
            self.load_plugin_modules(utils._splitstrip(config_data["load-plugins"]))

        self._parse_configuration_file(config_args)

        # Set the current module to the command line
        # to allow raising messages on it
        self.set_current_module(config_file)

        self._emit_stashed_messages()

        # Set the current module to configuration as we don't know where
        # the --load-plugins key is coming from
        self.set_current_module("Command line or configuration file")

        # We have loaded configuration from config file and command line. Now, we can
        # load plugin specific configuration.
        self.load_plugin_configuration()

        # Now that plugins are loaded, get list of all fail_on messages, and
        # enable them
        self.enable_fail_on_messages()

        self._parse_error_mode()

        # Link the base Namespace object on the current directory
        self._directory_namespaces[Path().resolve()] = (self.config, {})

        return True

    def _expand_files(self, modules):
        expanded = super()._expand_files(modules)
        filtered = {}
        # PyLinter._expand_files returns dict since 2.15.7.
        if packaging_version.parse(pylint_version) > packaging_version.parse("2.15.6"):
            for module in expanded:
                if not self._files.is_excluded(Path(module)):
                    filtered[module] = expanded[module]
            return filtered
        else:
            for module in expanded:
                # need to de-duplicate, as pylint also walks directories given to it, so it will find
                # files that prospector has already provided and end up checking it more than once
                if not self._files.is_excluded(Path(module["path"])):
                    # if the key exists, just overwrite it with the same value, so we don't need an extra if statement
                    filtered[module["path"]] = module
            return filtered.values()
