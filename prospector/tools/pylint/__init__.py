import os
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from pylint.config import find_default_config_files
from pylint.exceptions import UnknownMessageError
from pylint.lint.run import _cpu_count

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import ToolBase
from prospector.tools.pylint.collector import Collector
from prospector.tools.pylint.linter import ProspectorLinter

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig

_UNUSED_WILDCARD_IMPORT_RE = re.compile(r"^Unused import(\(s\))? (.*) from wildcard import")

_IGNORE_RE = re.compile(r"#\s*pylint:\s*disable=([^#]*[^#\s])(\s*#.*)?$", re.IGNORECASE)


def _is_in_dir(subpath: Path, path: Path) -> bool:
    return subpath.parent == path


class PylintTool(ToolBase):
    # There are several methods on this class which could technically
    # be functions (they don't use the 'self' argument) but that would
    # make this module/class a bit ugly.

    def __init__(self) -> None:
        self._args: Any = None
        self._collector: Optional[Collector] = None
        self._linter: Optional[ProspectorLinter] = None
        self._orig_sys_path: list[str] = []

    def _prospector_configure(self, prospector_config: "ProspectorConfig", linter: ProspectorLinter) -> list[Message]:
        errors = []

        if "django" in prospector_config.libraries:
            linter.load_plugin_modules(["pylint_django"])
        if "celery" in prospector_config.libraries:
            linter.load_plugin_modules(["pylint_celery"])
        if "flask" in prospector_config.libraries:
            linter.load_plugin_modules(["pylint_flask"])

        profile_path = os.path.join(prospector_config.workdir, prospector_config.profile.name)
        for plugin in prospector_config.profile.pylint.get("load-plugins", []):  # type: ignore[attr-defined]
            try:
                linter.load_plugin_modules([plugin])
            except ImportError:
                errors.append(self._error_message(profile_path, f"Could not load plugin {plugin}"))

        for msg_id in prospector_config.get_disabled_messages("pylint"):
            try:  # noqa: SIM105
                linter.disable(msg_id)
            except UnknownMessageError:
                # If the msg_id doesn't exist in PyLint any more,
                # don't worry about it.
                pass

        options = prospector_config.tool_options("pylint")

        for checker in linter.get_checkers():
            if not hasattr(checker, "options"):
                continue
            for option in checker.options:
                if option[0] in options:
                    checker._arguments_manager.set_option(  # pylint: disable=protected-access
                        option[0], options[option[0]]
                    )

        # The warnings about disabling warnings are useful for figuring out
        # with other tools to suppress messages from. For example, an unused
        # import which is disabled with 'pylint disable=unused-import' will
        # still generate an 'FL0001' unused import warning from pyflakes.
        # Using the information from these messages, we can figure out what
        # was disabled.
        linter.disable("locally-disabled")  # notification about disabling a message
        linter.enable("file-ignored")  # notification about disabling an entire file
        linter.enable("suppressed-message")  # notification about a message being suppressed
        linter.disable("deprecated-pragma")  # notification about use of deprecated 'pragma' option

        max_line_length = prospector_config.max_line_length
        for checker in linter.get_checkers():
            if not hasattr(checker, "options"):
                continue
            for option in checker.options:
                if max_line_length is not None and option[0] == "max-line-length":
                    checker._arguments_manager.set_option(  # pylint: disable=protected-access
                        "max-line-length", max_line_length
                    )
        return errors

    def _error_message(self, filepath: Union[str, Path], message: str) -> Message:
        location = Location(filepath, None, None, 0, 0)
        return Message("prospector", "config-problem", location, message)

    def _pylintrc_configure(self, pylintrc: Union[str, Path], linter: ProspectorLinter) -> list[Message]:
        errors = []
        are_plugins_loaded = linter.config_from_file(pylintrc)
        if not are_plugins_loaded and hasattr(linter.config, "load_plugins"):
            for plugin in linter.config.load_plugins:
                try:
                    linter.load_plugin_modules([plugin])
                except ImportError:
                    errors.append(self._error_message(pylintrc, f"Could not load plugin {plugin}"))
        return errors

    def configure(
        self, prospector_config: "ProspectorConfig", found_files: FileFinder
    ) -> Optional[tuple[Optional[Union[str, Path]], Optional[Iterable[Message]]]]:
        extra_sys_path = found_files.make_syspath()
        check_paths = self._get_pylint_check_paths(found_files)

        pylint_options = prospector_config.tool_options("pylint")
        self._set_path_finder(extra_sys_path, pylint_options)

        linter = ProspectorLinter(found_files)

        config_messages, configured_by = self._get_pylint_configuration(
            check_paths, linter, prospector_config, pylint_options
        )

        # we don't want similarity reports right now
        linter.disable("similarities")

        # use the collector 'reporter' to simply gather the messages
        # given by PyLint
        self._collector = Collector(linter.msgs_store)
        linter.set_reporter(self._collector)
        if linter.config.jobs == 0:
            linter.config.jobs = _cpu_count()
        self._linter = linter
        return configured_by, config_messages

    def _set_path_finder(self, extra_sys_path: list[Path], pylint_options: dict[str, Any]) -> None:
        # insert the target path into the system path to get correct behaviour
        self._orig_sys_path = sys.path
        if not pylint_options.get("use_pylint_default_path_finder"):
            sys.path = sys.path + [str(path.absolute()) for path in extra_sys_path]

    def _get_pylint_check_paths(self, found_files: FileFinder) -> list[Path]:
        # create a list of packages, but don't include packages which are
        # subpackages of others as checks will be duplicated
        check_paths = set()

        modules = found_files.python_modules
        packages = found_files.python_packages
        packages.sort(key=lambda p: len(str(p)))

        # don't add modules that are in known packages
        for module in modules:
            for package in packages:
                if _is_in_dir(module, package):
                    break
            else:
                check_paths.add(module)

        # sort from earlier packages first...
        for idx, package in enumerate(packages):
            # yuck o(n2) but... temporary
            for prev_pkg in packages[:idx]:
                if _is_in_dir(package, prev_pkg):
                    # this is a sub-package of a package we know about
                    break
            else:
                # we should care about this one
                check_paths.add(package)

        # need to sort to make sure multiple runs are deterministic
        return sorted(check_paths)

    def _get_pylint_configuration(
        self,
        check_paths: list[Path],
        linter: ProspectorLinter,
        prospector_config: "ProspectorConfig",
        pylint_options: dict[str, Any],
    ) -> tuple[list[Message], Optional[Union[Path, str]]]:
        self._args = check_paths
        linter.load_default_plugins()

        config_messages: list[Message] = self._prospector_configure(prospector_config, linter)
        configured_by: Optional[Union[str, Path]] = None

        if prospector_config.use_external_config("pylint"):
            # Try to find a .pylintrc
            pylintrc: Optional[Union[str, Path]] = pylint_options.get("config_file")
            external_config = prospector_config.external_config_location("pylint")

            pylintrc = pylintrc or external_config

            if pylintrc is None:
                for p in find_default_config_files():
                    pylintrc = str(p)
                    break

            if pylintrc is None:  # nothing explicitly configured
                for possible in (".pylintrc", "pylintrc", "pyproject.toml", "setup.cfg"):
                    pylintrc_path = os.path.join(prospector_config.workdir, possible)
                    # TODO: pyproject and setup.cfg might not actually have any pylint config
                    #       in, they should be skipped in that case
                    if os.path.exists(pylintrc_path):
                        pylintrc = pylintrc_path
                        break

            if pylintrc is not None:
                # load it!
                configured_by = pylintrc
                config_messages += self._pylintrc_configure(pylintrc, linter)

        return config_messages, configured_by

    def _combine_w0614(self, messages: list[Message]) -> list[Message]:
        """
        For the "unused import from wildcard import" messages,
        we want to combine all warnings about the same line into
        a single message.
        """
        by_loc = defaultdict(list)
        out = []

        for message in messages:
            if message.code == "unused-wildcard-import":
                by_loc[message.location].append(message)
            else:
                out.append(message)

        for location, message_list in by_loc.items():
            names = []
            for msg in message_list:
                match_ = _UNUSED_WILDCARD_IMPORT_RE.match(msg.message)
                assert match_ is not None
                names.append(match_.group(1))

            msgtxt = "Unused imports from wildcard import: {}".format(", ".join(names))
            combined_message = Message("pylint", "unused-wildcard-import", location, msgtxt)
            out.append(combined_message)

        return out

    def combine(self, messages: list[Message]) -> list[Message]:
        """
        Combine repeated messages.

        Some error messages are repeated, causing many errors where
        only one is strictly necessary.

        For example, having a wildcard import will result in one
        'Unused Import' warning for every unused import.
        This method will combine these into a single warning.
        """
        combined = self._combine_w0614(messages)
        return sorted(combined)

    def run(self, found_files: FileFinder) -> list[Message]:
        assert self._collector is not None
        assert self._linter is not None

        self._linter.check(self._args)
        sys.path = self._orig_sys_path

        messages = self._collector.get_messages()
        return self.combine(messages)

    def get_ignored_codes(self, line: str) -> list[str]:
        match = _IGNORE_RE.search(line)
        if match:
            return [e.strip() for e in match.group(1).split(",")]
        return []
