# -*- coding: utf-8 -*-
from __future__ import absolute_import

# HACK!
# pep257 version 0.4.1 sets global log level to debug
# which causes it to spaff the output with tokenizing
# information.
import pydocstyle  # noqa
if hasattr(pydocstyle, 'log'):  # noqa
    def dummy_log(*args, **kwargs):  # noqa
        pass
    pydocstyle.log.debug = dummy_log

from pydocstyle import PEP257Checker, AllError
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

    def configure(self, prospector_config, found_files):
        self.ignore_codes = prospector_config.get_disabled_messages('pep257')

    def run(self, found_files):
        messages = []

        checker = PEP257Checker()

        for code_file in found_files.iter_module_paths():
            try:
                for error in checker.check_source(
                        open(code_file, 'r').read(),
                        code_file,
                ):
                    location = Location(
                        path=code_file,
                        module=None,
                        function='',
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
                # pep257's Parser.parse_all method raises AllError when an
                # attempt to analyze the __all__ definition has failed.  This
                # occurs when __all__ is too complexed to be parsed.
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
                    message=exc.args[0],
                )
                messages.append(message)

        return self.filter_messages(messages)

    def filter_messages(self, messages):
        return [
            message
            for message in messages
            if message.code not in self.ignore_codes
        ]
