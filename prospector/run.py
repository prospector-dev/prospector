# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os.path
import sys
from datetime import datetime

from prospector import blender, postfilter, tools
from prospector.config import configuration as cfg
from prospector.config import ProspectorConfig
from prospector.exceptions import FatalProspectorException
from prospector.finder import find_python
from prospector.formatters import FORMATTERS
from prospector.message import Location, Message
from prospector.tools.utils import capture_output

__all__ = (
    'Prospector',
    'main',
)


class Prospector(object):
    def __init__(self, config):
        self.config = config
        self.summary = None
        self.messages = config.messages

    def process_messages(self, found_files, messages):
        for message in messages:
            if self.config.absolute_paths:
                message.to_absolute_path(self.config.workdir)
            else:
                message.to_relative_path(self.config.workdir)
        if self.config.blending:
            messages = blender.blend(messages)

        filepaths = found_files.iter_module_paths(abspath=False)
        return postfilter.filter_messages(filepaths, self.config.workdir, messages)

    def execute(self):

        summary = {
            'started': datetime.now(),
        }
        summary.update(self.config.get_summary_information())

        found_files = find_python(self.config.ignores, self.config.paths,
                                  self.config.explicit_file_mode, self.config.workdir)

        # Run the tools
        messages = []
        for tool in self.config.get_tools(found_files):
            for name, cls in tools.TOOLS.items():
                if cls == tool.__class__:
                    toolname = name
                    break
            else:
                toolname = 'Unknown'

            try:
                # Tools can output to stdout/stderr in unexpected places, for example,
                # pep257 emits warnings about __all__ and as pyroma exec's the setup.py
                # file, it will execute any print statements in that, etc etc...
                with capture_output(hide=not self.config.direct_tool_stdout) as capture:
                    messages += tool.run(found_files)

                    if self.config.include_tool_stdout:
                        loc = Location(self.config.workdir, None, None, None, None)

                        if capture.get_hidden_stderr():
                            msg = 'stderr from %s:\n%s' % (toolname, capture.get_hidden_stderr())
                            messages.append(Message(toolname, 'hidden-output', loc, message=msg))
                        if capture.get_hidden_stdout():
                            msg = 'stdout from %s:\n%s' % (toolname, capture.get_hidden_stdout())
                            messages.append(Message(toolname, 'hidden-output', loc, message=msg))

            except FatalProspectorException as fatal:
                sys.stderr.write(fatal.message)
                sys.exit(2)

            except Exception:  # pylint: disable=broad-except
                if self.config.die_on_tool_error:
                    raise
                else:
                    loc = Location(self.config.workdir, None, None, None, None)
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

        messages = self.process_messages(found_files, messages)

        summary['message_count'] = len(messages)
        summary['completed'] = datetime.now()

        # Timedelta.total_seconds() is not available
        # on Python<=2.6 so we calculate it ourselves
        # See issue #60 and http://stackoverflow.com/a/3694895
        delta = (summary['completed'] - summary['started'])
        total_seconds = (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 1e6) / 1e6
        summary['time_taken'] = '%0.2f' % total_seconds

        external_config = []
        for tool, configured_by in self.config.configured_by.items():
            if configured_by is not None:
                external_config.append((tool, configured_by))
        if len(external_config) > 0:
            summary['external_config'] = ', '.join(['%s: %s' % info for info in external_config])

        self.summary = summary
        self.messages = self.messages + messages

    def get_summary(self):
        return self.summary

    def get_messages(self):
        return self.messages

    def print_messages(self, write_to=None):
        write_to = write_to or sys.stdout

        output_format = self.config.get_output_format()
        self.summary['formatter'] = output_format
        formatter = FORMATTERS[output_format](self.summary, self.messages, self.config.profile)

        # Produce the output
        write_to.write(formatter.render(
            summary=not self.config.messages_only,
            messages=not self.config.summary_only,
            profile=self.config.show_profile
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
    config = ProspectorConfig()

    paths = config.paths
    if len(paths) > 1 and not all([os.path.isfile(path) for path in paths]):
        sys.stderr.write('\nIn multi-path mode, all inputs must be files, '
                         'not directories.\n\n')
        get_parser().print_usage()
        sys.exit(2)

    # Make it so
    prospector = Prospector(config)
    prospector.execute()
    prospector.print_messages()

    if config.exit_with_zero_on_success():
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
