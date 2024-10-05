import sys
import warnings
from pathlib import Path

from packaging import version as packaging_version
from pylint import version as pylint_version
from pylint.config.config_file_parser import _ConfigurationFileParser
from pylint.config.config_initialization import _order_all_first
from pylint.config.exceptions import _UnrecognizedOptionError
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

        unrecognized_options_message = None
        # First we parse any options from a configuration file
        try:
            self._parse_configuration_file(config_args)
        except _UnrecognizedOptionError as exc:
            unrecognized_options_message = ", ".join(exc.options)

        # Then, if a custom reporter is provided as argument, it may be overridden
        # by file parameters, so we re-set it here. We do this before command line
        # parsing, so it's still overridable by command line options
        # if reporter:
        #     self.set_reporter(reporter)

        # Set the current module to the command line
        # to allow raising messages on it
        self.set_current_module(config_file)

        # Now we parse any options from the command line, so they can override
        # the configuration file
        # args_list = _order_all_first(args_list, joined=True)
        # parsed_args_list = self._parse_command_line_configuration(args_list)

        # Remove the positional arguments separator from the list of arguments if it exists
        # try:
        #     parsed_args_list.remove("--")
        # except ValueError:
        #     pass

        # Check if there are any options that we do not recognize
        unrecognized_options: list[str] = []
        # for opt in parsed_args_list:
        #     if opt.startswith("--"):
        #         unrecognized_options.append(opt[2:])
        #     elif opt.startswith("-"):
        #         unrecognized_options.append(opt[1:])
        if unrecognized_options:
            msg = ", ".join(unrecognized_options)
            try:
                self._arg_parser.error(f"Unrecognized option found: {msg}")
            except SystemExit:
                sys.exit(32)

        # Now that config file and command line options have been loaded
        # with all disables, it is safe to emit messages
        if unrecognized_options_message is not None:
            self.set_current_module(str(config_file) if config_file else "")
            self.add_message("unrecognized-option", args=unrecognized_options_message, line=0)

        # TODO: Change this to be checked only when upgrading the configuration
        for exc_name in self.config.overgeneral_exceptions:
            if "." not in exc_name:
                warnings.warn_explicit(
                    f"'{exc_name}' is not a proper value for the 'overgeneral-exceptions' option. "
                    f"Use fully qualified name (maybe 'builtins.{exc_name}' ?) instead. "
                    "This will cease to be checked at runtime when the configuration "
                    "upgrader is released.",
                    category=UserWarning,
                    filename="pylint: Command line or configuration file",
                    lineno=1,
                    module="pylint",
                )

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
