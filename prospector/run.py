import os.path
import sys
import re

from datetime import datetime

from prospector import config as cfg, tools, blender
from prospector.adaptor import LIBRARY_ADAPTORS
from prospector.adaptor.common import CommonAdaptor
from prospector.adaptor.profile import ProfileAdaptor
from prospector.autodetect import autodetect_libraries
from prospector.formatters import FORMATTERS
from prospector.message import Location, Message
from prospector.finder import find_python


__all__ = (
    'Prospector',
    'main',
)


class Prospector(object):
    def __init__(self, config, path):
        self.config = config
        self.path = path
        self.adaptors = []
        self.libraries = []
        self.profiles = []
        self.profile_adaptor = None
        self.tool_runners = []
        self.ignores = []

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
        # Use the strictness profile
        if self.config.strictness:
            self.profiles.append('strictness_%s' % self.config.strictness)

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
        self.profiles += self.config.profiles

        self.profile_adaptor = ProfileAdaptor(self.profiles)
        self.adaptors.append(self.profile_adaptor)

    def _determine_tool_runners(self):
        for tool in self.config.tools:
            if self.profile_adaptor.is_tool_enabled(tool):
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
                message.to_absolute_path(self.path)
            else:
                message.to_relative_path(self.path)
        if self.config.blending:
            messages = blender.blend(messages)

        return messages

    def execute(self):
        summary = {
            'started': datetime.now(),
            'libraries': self.libraries,
            'strictness': self.config.strictness,
            'profiles': self.profiles,
            'adaptors': [adaptor.name for adaptor in self.adaptors],
            'tools': self.config.tools,
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

        return summary, messages


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
    summary, messages = prospector.execute()

    # Get the output formatter
    summary['formatter'] = config.output_format
    formatter = FORMATTERS[config.output_format](summary, messages)

    # Produce the output
    sys.stdout.write(formatter.render(
        summary=not config.messages_only,
        messages=not config.summary_only,
    ))
    sys.stdout.write('\n')

    if messages:
        return 1


if __name__ == '__main__':
    sys.exit(main())
