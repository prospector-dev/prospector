import os.path
import sys
import re

from datetime import datetime

from prospector import config as cfg, tools, blender, postfilter
from prospector.adaptor import LIBRARY_ADAPTORS
from prospector.adaptor.common import CommonAdaptor
from prospector.adaptor.profile import ProfileAdaptor
from prospector.autodetect import autodetect_libraries
from prospector.formatters import FORMATTERS
from prospector.message import Location, Message
from prospector.finder import find_python
from prospector.profiles.profile import ProfileNotFound
from prospector.tools import DEFAULT_TOOLS


__all__ = (
    'Prospector',
    'main',
)


class Prospector(object):
    def __init__(self, config, path):
        self.config = config
        self.path = path
        if os.path.isdir(path):
            self.rootpath = path
        else:
            self.rootpath = os.getcwd()
        self.adaptors = []
        self.libraries = []
        self.profiles = []
        self.profile_adaptor = None
        self.tool_runners = []
        self.ignores = []
        self.strictness = None
        self.tools_to_run = []

        self.summary = None
        self.messages = None

        self._determine_adapters()
        self._determine_profiles()
        self._determine_tool_runners()
        self._determine_ignores()

    def _determine_adapters(self):
        # Bring in the common adaptor
        if self.config.common_plugin:
            self.adaptors.append(CommonAdaptor())

        # Bring in adaptors that we automatically detect are needed
        if self.config.autodetect:
            for name, adaptor in autodetect_libraries(self.path):
                self.libraries.append(name)
                self.adaptors.append(adaptor)

        # Bring in adaptors for the specified libraries
        for name in self.config.uses:
            if name not in self.libraries:
                self.libraries.append(name)
                self.adaptors.append(LIBRARY_ADAPTORS[name]())

    def _determine_profiles(self):

        # Use other specialty profiles based on options
        if not self.config.doc_warnings:
            self.profiles.append('no_doc_warnings')
        if not self.config.test_warnings:
            self.profiles.append('no_test_warnings')
        if not self.config.style_warnings:
            self.profiles.append('no_pep8')
        if self.config.full_pep8:
            self.profiles.append('full_pep8')

        # Use the specified profiles
        profile_provided = False
        if len(self.config.profiles) > 0:
            profile_provided = True
        self.profiles += self.config.profiles

        # if there is a '.prospector.yaml' or a '.prospector/prospector.yaml'
        # file then we'll include that
        prospector_yaml = os.path.join(self.path, '.prospector.yaml')
        if os.path.exists(prospector_yaml) and os.path.isfile(prospector_yaml):
            profile_provided = True
            self.profiles.append(prospector_yaml)

        prospector_yaml = os.path.join(self.path, 'prospector', 'prospector.yaml')
        if os.path.exists(prospector_yaml) and os.path.isfile('prospector'):
            profile_provided = True
            self.profiles.append(prospector_yaml)

        if not profile_provided:
            # Use the strictness profile only if no profile has been given
            if self.config.strictness:
                self.profiles = ['strictness_%s' % self.config.strictness] + self.profiles
                self.strictness = self.config.strictness
        else:
            self.strictness = 'from profile'

        # the profile path is
        #   * anything provided as an argument
        #   * a directory called .prospector in the check path
        #   * the check path
        #   * prospector provided profiles
        profile_path = self.config.profile_path

        prospector_dir = os.path.join(self.path, '.prospector')
        if os.path.exists(prospector_dir) and os.path.isdir(prospector_dir):
            profile_path.append(prospector_dir)

        profile_path.append(self.path)

        provided = os.path.join(os.path.dirname(__file__), 'profiles/profiles')
        profile_path.append(provided)

        try:
            self.profile_adaptor = ProfileAdaptor(self.profiles, profile_path)
        except ProfileNotFound as nfe:
            sys.stderr.write("Failed to run:\nCould not find profile %s. Search path: %s\n" %
                             (nfe.name, ':'.join(nfe.profile_path)))
            sys.exit(1)

        self.adaptors.append(self.profile_adaptor)

    def _determine_tool_runners(self):

        if self.config.tools is None:
            # we had no command line settings for an explicit list of
            # tools, so we use the defaults
            to_run = set(DEFAULT_TOOLS)
            # we can also use any that the profiles dictate
            for tool in tools.TOOLS.keys():
                if self.profile_adaptor.is_tool_enabled(tool):
                    to_run.add(tool)
        else:
            to_run = set(self.config.tools)
            # profiles have no say in the list of tools run when
            # a command line is specified

        for tool in self.config.with_tools:
            to_run.add(tool)

        for tool in self.config.without_tools:
            to_run.remove(tool)

        if self.config.tools is None and len(self.config.with_tools) == 0 and len(self.config.without_tools) == 0:
            for tool in tools.TOOLS.keys():
                enabled = self.profile_adaptor.is_tool_enabled(tool)
                if enabled is None:
                    enabled = tool in DEFAULT_TOOLS
                if tool in to_run and not enabled:
                    to_run.remove(tool)

        self.tools_to_run = sorted(list(to_run))
        for tool in self.tools_to_run:
            self.tool_runners.append(tools.TOOLS[tool]())

    def _determine_ignores(self):
        # Grab ignore patterns from the profile adapter
        ignores = [
            re.compile(ignore)
            for ignore in self.profile_adaptor.profile.ignore
        ]

        # Grab ignore patterns from the options
        ignores += [
            re.compile(patt)
            for patt in self.config.ignore_patterns
        ]

        # Grab ignore paths from the options
        boundary = r"(^|/|\\)%s(/|\\|$)"
        ignores += [
            re.compile(boundary % re.escape(ignore_path))
            for ignore_path in self.config.ignore_paths
        ]

        # Add any specified by the other adaptors
        for adaptor in self.adaptors:
            if hasattr(adaptor.__class__, 'ignore_patterns'):
                ignores += [re.compile(p) for p in adaptor.ignore_patterns]

        self.ignores = ignores

    def process_messages(self, messages):
        for message in messages:
            if self.config.absolute_paths:
                message.to_absolute_path(self.rootpath)
            else:
                message.to_relative_path(self.rootpath)
        if self.config.blending:
            messages = blender.blend(messages)

        return postfilter.filter_messages(messages)

    def execute(self):

        summary = {
            'started': datetime.now(),
            'libraries': self.libraries,
            'strictness': self.strictness,
            'profiles': self.profiles,
            'adaptors': [adaptor.name for adaptor in self.adaptors],
            'tools': self.tools_to_run,
        }

        # Find the files and packages in a common way, so that each tool
        # gets the same list.
        found_files = find_python(self.ignores, self.path)

        # Prep the tools.
        for tool in self.tool_runners:
            tool.prepare(found_files, self.config, self.adaptors)

        # Run the tools
        messages = []
        for tool in self.tool_runners:
            try:
                messages += tool.run()
            except Exception:  # pylint: disable=W0703
                if self.config.die_on_tool_error:
                    raise
                else:
                    for name, cls in tools.TOOLS.items():
                        if cls == tool.__class__:
                            toolname = name
                            break
                    else:
                        toolname = 'Unknown'

                    loc = Location(self.path, None, None, None, None)
                    msg = 'Tool %s failed to run (exception was raised)' % (
                        toolname,
                    )
                    message = Message(
                        toolname,
                        'failure',
                        loc,
                        message=msg,
                    )
                    messages.append(message)

        messages = self.process_messages(messages)

        summary['message_count'] = len(messages)
        summary['completed'] = datetime.now()
        delta = (summary['completed'] - summary['started'])
        summary['time_taken'] = '%0.2f' % delta.total_seconds()

        self.summary = summary
        self.messages = messages

    def get_summary(self):
        return self.summary

    def get_messages(self):
        return self.messages

    def print_messages(self, write_to=None):
        write_to = write_to or sys.stdout

        # Get the output formatter
        if self.config.output_format is not None:
            output_format = self.config.output_format
        else:
            output_format = self.profile_adaptor.get_output_format()

        if output_format is None:
            output_format = 'text'

        self.summary['formatter'] = output_format
        formatter = FORMATTERS[output_format](self.summary, self.messages)

        # Produce the output
        write_to.write(formatter.render(
            summary=not self.config.messages_only,
            messages=not self.config.summary_only,
        ))
        write_to.write('\n')


def get_parser():
    """
    This is a helper method to return an argparse parser, to
    be used with the Sphinx argparse plugin for documentation.
    """
    manager = cfg.build_manager()
    source = cfg.build_command_line_source(prog='prospector', description=None)
    return source.build_parser(manager.settings, None)


def main():
    # Get our configuration
    mgr = cfg.build_manager()
    config = mgr.retrieve(*cfg.build_default_sources())

    # Figure out what paths we're prospecting
    if config['path']:
        paths = [config['path']]
    elif mgr.arguments['checkpath']:
        paths = mgr.arguments['checkpath']
    else:
        paths = [os.getcwd()]

    # Make it so
    prospector = Prospector(config, paths[0])
    prospector.execute()
    prospector.print_messages()

    if config.zero_exit:
        # if we ran successfully, and the user wants us to, then we'll
        # exit cleanly
        return 0

    # otherwise, finding messages is grounds for exiting with an error
    # code, to make it easier for bash scripts and similar situations
    # to know if there any errors have been found.
    if len(prospector.get_messages()) > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
