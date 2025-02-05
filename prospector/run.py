import argparse
import codecs
import os.path
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TextIO

from prospector import blender, postfilter, tools
from prospector.compat import is_relative_to
from prospector.config import ProspectorConfig
from prospector.config import configuration as cfg
from prospector.exceptions import FatalProspectorException
from prospector.finder import FileFinder
from prospector.formatters import FORMATTERS, Formatter
from prospector.message import Location, Message
from prospector.tools import DEPRECATED_TOOL_NAMES
from prospector.tools.base import ToolBase
from prospector.tools.utils import CaptureOutput


class Prospector:
    def __init__(self, config: ProspectorConfig) -> None:
        self.config = config
        self.summary: Optional[dict[str, Any]] = None
        self.messages = config.messages

    def process_messages(
        self, found_files: FileFinder, messages: list[Message], tools: dict[str, tools.ToolBase]
    ) -> list[Message]:
        if self.config.blending:
            messages = blender.blend(messages)

        if self.config.legacy_tool_names:
            updated = []
            new_names = {v: k for k, v in DEPRECATED_TOOL_NAMES.items()}
            for msg in messages:
                msg.source = new_names.get(msg.source, msg.source)
                updated.append(msg)
            messages = updated

        return postfilter.filter_messages(found_files.python_modules, messages, tools, self.config.blending)

    def execute(self) -> None:
        deprecated_names = self.config.replace_deprecated_tool_names()

        summary: dict[str, Any] = {
            "started": datetime.now(),
        }
        summary.update(self.config.get_summary_information())

        paths = [Path(p) for p in self.config.paths]
        found_files = FileFinder(*paths, exclusion_filters=[self.config.make_exclusion_filter()])
        messages = []

        # see if any old tool names are run
        for deprecated_name in deprecated_names:
            loc = Location(self.config.workdir, None, None, None, None)
            new_name = DEPRECATED_TOOL_NAMES[deprecated_name]
            msg = (
                f"Tool {deprecated_name} has been renamed to {new_name}. "
                f"The old name {deprecated_name} is now deprecated and will be removed in Prospector 2.0. "
                f"Please update your prospector configuration."
            )

            message = Message(
                "prospector",
                "Deprecation",
                loc,
                message=msg,
            )
            messages.append(message)
            warnings.warn(msg, category=DeprecationWarning, stacklevel=0)

        running_tools: dict[str, ToolBase] = {}

        # Run the tools
        for tool in self.config.get_tools(found_files):
            for name, cls in tools.TOOLS.items():
                if cls == tool.__class__:
                    toolname = name
                    break
            else:
                toolname = "Unknown"

            running_tools[toolname] = tool

            try:
                # Tools can output to stdout/stderr in unexpected places, for example,
                # pydocstyle emits warnings about __all__ and as pyroma exec's the setup.py
                # file, it will execute any print statements in that, etc etc...
                with CaptureOutput(hide=not self.config.direct_tool_stdout) as capture:
                    messages += tool.run(found_files)

                    if self.config.include_tool_stdout:
                        loc = Location(self.config.workdir, None, None, None, None)

                        if capture.get_hidden_stderr():
                            msg = f"stderr from {toolname}:\n{capture.get_hidden_stderr()}"
                            messages.append(Message(toolname, "hidden-output", loc, message=msg))
                        if capture.get_hidden_stdout():
                            msg = f"stdout from {toolname}:\n{capture.get_hidden_stdout()}"
                            messages.append(Message(toolname, "hidden-output", loc, message=msg))

            except FatalProspectorException as fatal:
                sys.stderr.write(str(fatal))
                sys.exit(2)

            except Exception as ex:  # pylint:disable=broad-except
                if self.config.die_on_tool_error:
                    raise FatalProspectorException(f"Tool {toolname} failed to run.") from ex
                loc = Location(self.config.workdir, None, None, None, None)
                msg = (
                    f"Tool {toolname} failed to run "
                    f"(exception was raised, re-run prospector with -X to see the stacktrace)"
                )
                message = Message(
                    toolname,
                    "failure",
                    loc,
                    message=msg,
                )
                messages.append(message)

        messages = self.process_messages(found_files, messages, running_tools)

        summary["message_count"] = len(messages)
        summary["completed"] = datetime.now()

        delta = summary["completed"] - summary["started"]
        summary["time_taken"] = f"{delta.total_seconds():0.2f}"

        external_config = []
        for tool_name, configured_by in self.config.configured_by.items():
            if configured_by is not None:
                external_config.append((tool_name, configured_by))
        if len(external_config) > 0:
            summary["external_config"] = ", ".join(["{}: {}".format(*info) for info in external_config])

        self.summary = summary
        self.messages = self.messages + messages

    def get_summary(self) -> Optional[dict[str, Any]]:
        return self.summary

    def get_messages(self) -> list[Message]:
        return self.messages

    def print_messages(self) -> None:
        output_reports = self.config.get_output_report()

        for report in output_reports:
            assert self.summary is not None
            output_format, output_files = report
            self.summary["formatter"] = output_format

            relative_to = None
            # use relative paths by default unless explicitly told otherwise (with a --absolute-paths flag)
            # or if some paths passed to prospector are not relative to the CWD
            if not self.config.absolute_paths and all(
                is_relative_to(p, self.config.workdir) for p in self.config.paths
            ):
                relative_to = self.config.workdir

            formatter = FORMATTERS[output_format](self.summary, self.messages, self.config.profile, relative_to)
            if not output_files and not self.config.quiet:
                self.write_to(formatter, sys.stdout)
            for output_file in output_files:
                with codecs.open(output_file, "w+") as target:
                    self.write_to(formatter, target)

    def write_to(self, formatter: Formatter, target: TextIO) -> None:
        # Produce the output
        target.write(
            formatter.render(
                summary=not self.config.messages_only,
                messages=not self.config.summary_only,
                profile=self.config.show_profile,
            )
        )
        target.write("\n")


def get_parser() -> argparse.ArgumentParser:
    """
    This is a helper method to return an argparse parser, to
    be used with the Sphinx argparse plugin for documentation.
    """
    manager = cfg.build_manager()
    source = cfg.build_command_line_source(prog="prospector", description=None)
    return source.build_parser(manager.settings, None)


def main() -> None:
    # Get our configuration
    config = ProspectorConfig()

    paths = config.paths
    if len(paths) > 1 and not all(os.path.isfile(path) for path in paths):
        sys.stderr.write("\nIn multi-path mode, all inputs must be files, not directories.\n\n")
        get_parser().print_usage()
        sys.exit(2)

    # Make it so
    prospector = Prospector(config)
    prospector.execute()
    prospector.print_messages()

    if config.exit_with_zero_on_success():
        # if we ran successfully, and the user wants us to, then we'll
        # exit cleanly
        sys.exit(0)

    # otherwise, finding messages is grounds for exiting with an error
    # code, to make it easier for bash scripts and similar situations
    # to know if any errors have been found.
    if len(prospector.get_messages()) > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
