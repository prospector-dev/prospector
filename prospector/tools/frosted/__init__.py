from __future__ import absolute_import

from frosted.api import iter_source_code, check_path

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'FrostedTool',
)


class ProspectorReporter(object):
    def __init__(self, ignore=None):
        self._messages = []
        self.ignore = ignore or ()

    # pylint: disable=R0913
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
        self._paths = []
        self._ignores = []

    def prepare(self, rootpath, ignore, args, adaptors):
        self._paths = [rootpath]
        self._ignores = ignore

        for adaptor in adaptors:
            adaptor.adapt_frosted(self)

    def run(self):
        reporter = ProspectorReporter(ignore=self.ignore_codes)

        for filepath in iter_source_code(self._paths):
            if any([ip.search(filepath) for ip in self._ignores]):
                continue

            check_path(filepath, reporter)

        return reporter.get_messages()
