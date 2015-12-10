# -*- coding: utf-8 -*-
from __future__ import absolute_import

from frosted.api import check_path

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'FrostedTool',
)


class ProspectorReporter(object):
    def __init__(self, ignore=None):
        self._messages = []
        self.ignore = ignore or ()

    # pylint: disable=too-many-arguments
    def record_message(
            self,
            filename=None,
            line=None,
            character=None,
            code=None,
            message=None):

        if code in self.ignore:
            return

        location = Location(
            path=filename,
            module=None,
            function=None,
            line=line,
            character=character,
        )
        message = Message(
            source='frosted',
            code=code,
            location=location,
            message=message,
        )
        self._messages.append(message)

    def unexpected_error(self, filename, msg):
        self.record_message(
            filename=filename,
            code='U999',
            message=msg,
        )

    def flake(self, message):
        filename, _, msg = message.message.split(':', 2)

        self.record_message(
            filename=filename,
            line=message.lineno,
            character=(message.col + 1),
            code=message.type.error_code,
            message=msg,
        )

    def get_messages(self):
        return self._messages


class FrostedTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(FrostedTool, self).__init__(*args, **kwargs)
        self.ignore_codes = ()

    def configure(self, prospector_config, _):
        self.ignore_codes = prospector_config.get_disabled_messages('frosted')

    def run(self, found_files):
        reporter = ProspectorReporter(ignore=self.ignore_codes)

        for filepath in found_files.iter_module_paths():
            # Frosted cannot handle non-utf-8 encoded files at the moment -
            # see https://github.com/timothycrosley/frosted/issues/53
            # Therefore (since pyflakes overlaps heavily and does not have the same
            # problem) we will simply suppress that error. If you do get it working
            # correctly, you only end up with a "CannotDecodeFile" error anyway which
            # is not useful to the user of prospector, nor is it actually a problem
            # of the file but rather of frosted.
            try:
                check_path(filepath, reporter)
            except UnicodeDecodeError:
                # pylint:disable=pointless-except
                pass

        return reporter.get_messages()
