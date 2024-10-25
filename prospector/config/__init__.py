import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Optional, Union

import setoptconf.config

from prospector.finder import FileFinder

try:  # Python >= 3.11
    import re._constants as sre_constants
except ImportError:
    import sre_constants  # pylint: disable=deprecated-module

import contextlib

from prospector import tools
from prospector.autodetect import autodetect_libraries
from prospector.compat import is_relative_to
from prospector.config import configuration as cfg
from prospector.message import Message
from prospector.profiles import AUTO_LOADED_PROFILES
from prospector.profiles.profile import BUILTIN_PROFILE_PATH, CannotParseProfile, ProfileNotFound, ProspectorProfile
from prospector.tools import DEFAULT_TOOLS, DEPRECATED_TOOL_NAMES


class ProspectorConfig:
    # There are several methods on this class which could technically
    # be functions (they don't use the 'self' argument) but that would
    # make this module/class a bit ugly.
    # Also the 'too many instance attributes' warning is ignored, as this
    # is a config object and its sole purpose is to hold many properties!

    def __init__(self, workdir: Optional[Path] = None):
        self.config, self.arguments = self._configure_prospector()
        self.paths = self._get_work_path(self.config, self.arguments)
        self.explicit_file_mode = all(p.is_file for p in self.paths)
        self.workdir = workdir or Path.cwd()

        self.profile, self.strictness = self._get_profile(self.workdir, self.config)
        self.libraries = self._find_used_libraries(self.config, self.profile)
        self.tools_to_run = self._determine_tool_runners(self.config, self.profile)
        self.ignores = self._determine_ignores(self.config, self.profile, self.libraries)
        self.configured_by: dict[str, Optional[Union[str, Path]]] = {}
        self.messages: list[Message] = []

    def make_exclusion_filter(self) -> Callable[[Path], bool]:
        # Only close over the attributes required by the filter, rather
        # than the entire self, because ProspectorConfig can't be pickled
        # because of the config attribute, which would break parallel
        # pylint.
        ignores, workdir = self.ignores, self.workdir

        def _filter(path: Path) -> bool:
            for ignore in ignores:
                # first figure out where the path is, relative to the workdir
                # ignore-paths/patterns will usually be relative to a repository
                # root or the CWD, but the path passed to prospector may not be
                path = path.resolve().absolute()
                if is_relative_to(path, workdir):
                    path = path.relative_to(workdir)
                if ignore.match(str(path)):
                    return True
            return False

        return _filter

    def get_tools(self, found_files: FileFinder) -> list[tools.ToolBase]:
        self.configured_by = {}
        runners = []
        for tool_name in self.tools_to_run:
            tool = tools.TOOLS[tool_name]()
            config_result = tool.configure(self, found_files)
            messages: list[Message] = []
            configured_by = None
            if config_result is not None:
                configured_by, config_messages = config_result
                if config_messages is not None:
                    messages = list(config_messages)

            self.configured_by[tool_name] = configured_by
            self.messages += messages
            runners.append(tool)
        return runners

    def replace_deprecated_tool_names(self) -> list[str]:
        # pep8 was renamed pycodestyle ; pep257 was renamed pydocstyle
        # for backwards compatibility, these have been deprecated but will remain until prospector v2
        deprecated_found = []
        replaced = []
        for tool_name in self.tools_to_run:
            if tool_name in DEPRECATED_TOOL_NAMES:
                replaced.append(DEPRECATED_TOOL_NAMES[tool_name])
                deprecated_found.append(tool_name)
            else:
                replaced.append(tool_name)
        self.tools_to_run = replaced
        return deprecated_found

    def get_output_report(self) -> list[tuple[str, list[str]]]:
        # Get the output formatter
        output_report: list[tuple[str, list[str]]]
        if self.config.output_format is not None:
            output_report = self.config.output_format
        else:
            output_report = [(self.profile.output_format, self.profile.output_target)]  # type: ignore[list-item]

        for index, report in enumerate(output_report):
            if not all(report):
                output_report[index] = (report[0] or "grouped", report[1] or [])

        return output_report

    def _configure_prospector(self) -> tuple[setoptconf.config.Configuration, dict[str, str]]:
        # first we will configure prospector as a whole
        mgr = cfg.build_manager()
        config = mgr.retrieve(*cfg.build_default_sources())
        return config, mgr.arguments

    def _get_work_path(self, config: setoptconf.config.Configuration, arguments: dict[str, str]) -> list[Path]:
        # Figure out what paths we're prospecting
        if config["path"]:
            paths = [Path(self.config["path"])]
        elif arguments["checkpath"]:
            paths = [Path(p) for p in arguments["checkpath"]]
        else:
            paths = [Path.cwd()]
        return [p.resolve() for p in paths]

    def _get_profile(
        self, workdir: Path, config: setoptconf.config.Configuration
    ) -> tuple[ProspectorProfile, Optional[str]]:
        # Use the specified profiles
        profile_provided = False
        if len(config.profiles) > 0:
            profile_provided = True
        cmdline_implicit = []

        # if there is a '.prospector.ya?ml' or a '.prospector/prospector.ya?ml' or equivalent landscape config
        # file then we'll include that
        profile_name: Union[None, str, Path] = None
        if not profile_provided:
            for possible_profile in AUTO_LOADED_PROFILES:
                prospector_yaml = os.path.join(workdir, possible_profile)
                if os.path.exists(prospector_yaml) and os.path.isfile(prospector_yaml):
                    profile_provided = True
                    profile_name = possible_profile
                    break

        strictness = None

        if profile_provided:
            if profile_name is None:
                profile_name = config.profiles[0]
                extra_profiles = config.profiles[1:]
            else:
                extra_profiles = config.profiles

            strictness = "from profile"
        else:
            # Use the preconfigured prospector profiles
            profile_name = "default"
            extra_profiles = []

        if config.doc_warnings is not None and config.doc_warnings:
            cmdline_implicit.append("doc_warnings")
        if config.test_warnings is not None and config.test_warnings:
            cmdline_implicit.append("test_warnings")
        if config.no_style_warnings is not None and config.no_style_warnings:
            cmdline_implicit.append("no_pep8")
        if config.full_pep8 is not None and config.full_pep8:
            cmdline_implicit.append("full_pep8")
        if config.member_warnings is not None and config.member_warnings:
            cmdline_implicit.append("member_warnings")

        # Use the strictness profile only if no profile has been given
        if config.strictness is not None and config.strictness:
            cmdline_implicit.append(f"strictness_{config.strictness}")
            strictness = config.strictness

        # the profile path is
        #   * anything provided as an argument
        #   * a directory called .prospector in the check path
        #   * the check path
        #   * prospector provided profiles
        profile_path = [Path(path).absolute() for path in config.profile_path]

        prospector_dir = workdir / ".prospector"
        if os.path.exists(prospector_dir) and os.path.isdir(prospector_dir):
            profile_path.append(prospector_dir)

        profile_path.append(workdir)
        profile_path.append(BUILTIN_PROFILE_PATH)

        try:
            forced_inherits = cmdline_implicit + extra_profiles
            profile = ProspectorProfile.load(profile_name, profile_path, forced_inherits=forced_inherits)
        except CannotParseProfile as cpe:
            sys.stderr.write(
                "\n".join(
                    [
                        "Failed to run:",
                        f"Could not parse profile {cpe.filepath} as it is not valid YAML",
                        f"{cpe.get_parse_message()}",
                        "",
                    ]
                )
            )
            sys.exit(1)
        except ProfileNotFound as nfe:
            search_path = ":".join(map(str, nfe.profile_path))
            module_name = nfe.name.split(":")[0]
            sys.stderr.write(
                f"""Failed to run:
Could not find profile {nfe.name}.
Search path: {search_path}, or in module 'prospector_profile_{module_name}'
"""
            )
            sys.exit(1)
        else:
            return profile, strictness

    def _find_used_libraries(self, config: setoptconf.config.Configuration, profile: ProspectorProfile) -> list[str]:
        libraries = []

        # Bring in adaptors that we automatically detect are needed
        if config.autodetect and profile.autodetect is True:
            for found_dep in autodetect_libraries(self.workdir):
                libraries.append(found_dep)

        # Bring in adaptors for the specified libraries
        for name in set(config.uses + profile.uses):
            if name not in libraries:
                libraries.append(name)

        return libraries

    def _determine_tool_runners(self, config: setoptconf.config.Configuration, profile: ProspectorProfile) -> list[str]:
        if config.tools is None:
            # we had no command line settings for an explicit list of
            # tools, so we use the defaults
            to_run = set(DEFAULT_TOOLS)
            # we can also use any that the profiles dictate
            for tool in tools.TOOLS:
                if profile.is_tool_enabled(tool):
                    to_run.add(tool)
        else:
            to_run = set(config.tools)
            # profiles have no say in the list of tools run when
            # a command line is specified

        for tool in config.with_tools:
            to_run.add(tool)

        for tool in config.without_tools:
            if tool in to_run:
                to_run.remove(tool)

        # if config.tools is None and len(config.with_tools) == 0 and len(config.without_tools) == 0:
        for tool in tools.TOOLS:
            enabled = profile.is_tool_enabled(tool)
            if enabled is None:
                enabled = tool in DEFAULT_TOOLS
            if tool in to_run and not enabled and tool not in config.with_tools and tool not in (config.tools or []):
                # if this is not enabled in a profile but is asked for in a command line arg, we keep it, otherwise
                # remove it from the list to run
                to_run.remove(tool)

        return sorted(list(to_run))

    def _determine_ignores(
        self, config: setoptconf.config.Configuration, profile: ProspectorProfile, libraries: list[str]
    ) -> list[re.Pattern[str]]:
        # Grab ignore patterns from the options
        ignores = []
        for pattern in config.ignore_patterns + profile.ignore_patterns:
            if pattern is None:
                # this can happen if someone has a profile with an empty ignore-patterns value, eg:
                #
                #  ignore-patterns:
                #  uses: django
                continue
            with contextlib.suppress(sre_constants.error):
                ignores.append(re.compile(pattern))

        # Convert ignore paths into patterns
        boundary = r"(^|/|\\)%s(/|\\|$)"
        for ignore_path in config.ignore_paths + profile.ignore_paths:
            ignore_path = str(ignore_path)
            if ignore_path.endswith("/") or ignore_path.endswith("\\"):
                ignore_path = ignore_path[:-1]
            ignores.append(re.compile(boundary % re.escape(ignore_path)))

        # some libraries have further automatic ignores
        if "django" in libraries:
            ignores += [re.compile("(^|/)(south_)?migrations(/|$)")]

        return ignores

    def get_summary_information(self) -> dict[str, Any]:
        return {
            "libraries": self.libraries,
            "strictness": self.strictness,
            "profiles": ", ".join(self.profile.list_profiles()),
            "tools": self.tools_to_run,
        }

    def exit_with_zero_on_success(self) -> bool:
        return self.config.zero_exit

    def get_disabled_messages(self, tool_name: str) -> list[str]:
        return self.profile.get_disabled_messages(tool_name)

    def get_enabled_messages(self, tool_name: str) -> list[str]:
        return self.profile.get_enabled_messages(tool_name)

    def use_external_config(self, _: Any) -> bool:
        # Currently there is only one single global setting for whether to use
        # global config, but this could be extended in the future
        return not self.config.no_external_config

    def tool_options(self, tool_name: str) -> dict[str, Any]:
        tool = getattr(self.profile, tool_name, None)
        if tool is None:
            return {}
        return tool.get("options", {})

    def external_config_location(self, tool_name: str) -> Optional[Path]:
        return getattr(self.config, f"{tool_name}_config_file", None)

    @property
    def die_on_tool_error(self) -> bool:
        return self.config.die_on_tool_error

    @property
    def summary_only(self) -> bool:
        return self.config.summary_only

    @property
    def messages_only(self) -> bool:
        return self.config.messages_only

    @property
    def quiet(self) -> bool:
        return self.config.quiet

    @property
    def blending(self) -> bool:
        return self.config.blending

    @property
    def absolute_paths(self) -> bool:
        return self.config.absolute_paths

    @property
    def max_line_length(self) -> int:
        return self.config.max_line_length

    @property
    def include_tool_stdout(self) -> bool:
        return self.config.include_tool_stdout

    @property
    def direct_tool_stdout(self) -> bool:
        return self.config.direct_tool_stdout

    @property
    def show_profile(self) -> bool:
        return self.config.show_profile

    @property
    def legacy_tool_names(self) -> bool:
        return self.config.legacy_tool_names
