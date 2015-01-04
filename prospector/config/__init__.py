import os
import re
import sys
from prospector import tools
from prospector.autodetect import autodetect_libraries
from prospector.config import configuration as cfg
from prospector.profiles.profile import load_profiles, ProfileNotFound
from prospector.tools import DEFAULT_TOOLS


class ProspectorConfig(object):
    # There are several methods on this class which could technically
    # be functions (they don't use the 'self' argument) but that would
    # make this module/class a bit ugly.
    # Also the 'too many instance attributes' warning is ignored, as this
    # is a config object and its sole purpose is to hold many properties!
    # pylint:disable=no-self-use,too-many-instance-attributes

    def __init__(self):
        self.config, self.arguments = self._configure_prospector()

        self.paths = self._get_work_path(self.config, self.arguments)
        self.explicit_file_mode = all(map(os.path.isfile, self.paths))

        if os.path.isdir(self.paths[0]):
            self.workdir = self.paths[0]
        else:
            self.workdir = os.getcwd()

        self.profile, self.profile_names, self.strictness = self._get_profile(self.workdir, self.config)
        self.libraries = self._find_used_libraries(self.config)
        self.tools_to_run = self._determine_tool_runners(self.config, self.profile)
        self.ignores = self._determine_ignores(self.config, self.profile, self.libraries)
        self.configured_by = {}

    def get_tools(self, found_files):
        self.configured_by = {}
        runners = []
        for tool_name in self.tools_to_run:
            tool = tools.TOOLS[tool_name]()
            self.configured_by[tool] = tool.configure(self, found_files)
            runners.append(tool)
        return runners

    def get_output_format(self):
        # Get the output formatter
        if self.config.output_format is not None:
            output_format = self.config.output_format
        else:
            output_format = self.profile.output_format

        if output_format is None:
            output_format = 'grouped'

        return output_format

    def _configure_prospector(self):
        # first we will configure prospector as a whole
        mgr = cfg.build_manager()
        config = mgr.retrieve(*cfg.build_default_sources())
        return config, mgr.arguments

    def _get_work_path(self, config, arguments):
        # Figure out what paths we're prospecting
        if config['path']:
            paths = [self.config['path']]
        elif arguments['checkpath']:
            paths = arguments['checkpath']
        else:
            paths = [os.getcwd()]
        return paths

    def _get_profile(self, path, config):
        # Use other specialty profiles based on options
        profile_names = []

        if not config.doc_warnings:
            profile_names.append('no_doc_warnings')
        if not config.test_warnings:
            profile_names.append('no_test_warnings')
        if not config.style_warnings:
            profile_names.append('no_pep8')
        if config.full_pep8:
            profile_names.append('full_pep8')

        # Use the specified profiles
        profile_provided = False
        if len(config.profiles) > 0:
            profile_provided = True
        profile_names += config.profiles

        # if there is a '.prospector.ya?ml' or a '.prospector/prospector.ya?ml'
        # file then we'll include that
        poss_profs = (
            ('.prospector.yaml',),
            ('.prospector.yml',),
            ('prospector', '.prospector.yaml'),
            ('prospector', '.prospector.yml'),
        )

        for possible_profile in poss_profs:
            prospector_yaml = os.path.join(path, *possible_profile)  # pylint:disable=star-args
            if os.path.exists(prospector_yaml) and os.path.isfile(prospector_yaml):
                profile_provided = True
                profile_names.append(prospector_yaml)

        strictness = None

        if not profile_provided:
            # Use the strictness profile only if no profile has been given
            if config.strictness:
                profile_names = ['strictness_%s' % config.strictness] + profile_names
                strictness = config.strictness
        else:
            strictness = 'from profile'

        # the profile path is
        #   * anything provided as an argument
        #   * a directory called .prospector in the check path
        #   * the check path
        #   * prospector provided profiles
        profile_path = config.profile_path

        prospector_dir = os.path.join(path, '.prospector')
        if os.path.exists(prospector_dir) and os.path.isdir(prospector_dir):
            profile_path.append(prospector_dir)

        profile_path.append(path)

        provided = os.path.join(os.path.dirname(__file__), '../profiles/profiles')
        profile_path.append(provided)

        try:
            profile = load_profiles(profile_names, profile_path)
        except ProfileNotFound as nfe:
            sys.stderr.write("Failed to run:\nCould not find profile %s. Search path: %s\n" %
                             (nfe.name, ':'.join(nfe.profile_path)))
            sys.exit(1)
        else:
            return profile, profile_names, strictness

    def _find_used_libraries(self, config):
        libraries = []

        # Bring in adaptors that we automatically detect are needed
        if config.autodetect:
            map(libraries.append, autodetect_libraries(self.workdir))

        # Bring in adaptors for the specified libraries
        for name in config.uses:
            if name not in libraries:
                libraries.append(name)

        return libraries

    def _determine_tool_runners(self, config, profile):

        if config.tools is None:
            # we had no command line settings for an explicit list of
            # tools, so we use the defaults
            to_run = set(DEFAULT_TOOLS)
            # we can also use any that the profiles dictate
            for tool in tools.TOOLS.keys():
                if profile.is_tool_enabled(tool):
                    to_run.add(tool)
        else:
            to_run = set(config.tools)
            # profiles have no say in the list of tools run when
            # a command line is specified

        for tool in config.with_tools:
            to_run.add(tool)

        for tool in config.without_tools:
            to_run.remove(tool)

        if config.tools is None and len(config.with_tools) == 0 and len(config.without_tools) == 0:
            for tool in tools.TOOLS.keys():
                enabled = profile.is_tool_enabled(tool)
                if enabled is None:
                    enabled = tool in DEFAULT_TOOLS
                if tool in to_run and not enabled:
                    to_run.remove(tool)

        return sorted(list(to_run))

    def _determine_ignores(self, config, profile, libraries):
        # Grab ignore patterns from the profile adapter
        ignores = [
            re.compile(ignore)
            for ignore in profile.ignore
        ]

        # Grab ignore patterns from the options
        ignores += [
            re.compile(patt)
            for patt in config.ignore_patterns
        ]

        # Grab ignore paths from the options
        boundary = r"(^|/|\\)%s(/|\\|$)"
        ignores += [
            re.compile(boundary % re.escape(ignore_path))
            for ignore_path in config.ignore_paths
        ]

        # some libraries have further automatic ignores
        if 'django' in libraries:
            ignores += [
                re.compile('(^|/)(south_)?migrations(/|$)')
            ]

        return ignores

    def get_summary_information(self):
        return {
            'libraries': self.libraries,
            'strictness': self.strictness,
            'profiles': self.profile_names,
            'tools': self.tools_to_run,
        }

    def exit_with_zero_on_success(self):
        return self.config.zero_exit

    def get_disabled_messages(self, tool_name):
        return self.profile.get_disabled_messages(tool_name)

    def use_external_config(self, _):
        # Currently there is only one single global setting for whether to use
        # global config, but this could be extended in the future
        return not self.config.no_external_config

    def tool_options(self, tool_name):
        tool = getattr(self.profile, tool_name, None)
        if tool is None:
            return {}
        return tool.get('options', {})

    def external_config_location(self, tool_name):
        return getattr(self.config, '%s_config_file' % tool_name, None)

    @property
    def die_on_tool_error(self):
        return self.config.die_on_tool_error

    @property
    def summary_only(self):
        return self.config.summary_only

    @property
    def messages_only(self):
        return self.config.messages_only

    @property
    def blending(self):
        return self.config.blending

    @property
    def absolute_paths(self):
        return self.config.absolute_paths

    @property
    def max_line_length(self):
        return self.arguments.get('max_line_length', None)

    @property
    def loquacious_pylint(self):
        return self.config.loquacious_pylint
