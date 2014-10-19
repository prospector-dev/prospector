from __future__ import absolute_import

import os.path

from pep257 import PEP257Checker, AllError

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'Pep257Tool',
)


class Pep257Tool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(Pep257Tool, self).__init__(*args, **kwargs)
        self._code_files = []
        self.ignore_codes = ()

    def prepare(self, found_files, args, adaptors):
        self._code_files = list(found_files.iter_module_paths())

        for adaptor in adaptors:
            adaptor.adapt_pep257(self)

    def run(self):
        messages = []

        checker = PEP257Checker()

        for code_file in self._code_files:
            try:
                for error in checker.check_source(
                        open(code_file, 'r').read(),
                        code_file,
                        ):
                    location = Location(
                        path=code_file,
                        module=None,
                        function='dunno',
                        line=error.line,
                        character=0,
                        absolute_path=True,
                    )
                    message = Message(
                        source='pep257',
                        code=error.code,
                        location=location,
                        message=error.message.partition(':')[2].strip(),
                    )
                    messages.append(message)
            except AllError as exc:
                location = Location(
                    path=code_file,
                    module=None,
                    function=None,
                    line=1,
                    character=0,
                    absolute_path=True,
                )
                message = Message(
                    source='pep257',
                    code='D000',
                    location=location,
                    message=exc.message,
                )
                messages.append(message)

        return self.filter_messages(messages)

    def filter_messages(self, messages):
        return [
            message
            for message in messages
            if message.code not in self.ignore_codes
        ]
