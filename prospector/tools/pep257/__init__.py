# -*- coding: utf-8 -*-
from __future__ import absolute_import

from prospector.encoding import read_py_file, CouldNotHandleEncoding
from pydocstyle.checker import ConventionChecker as PEP257Checker, AllError
from prospector.message import Location, Message, make_tool_error_message
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
                    read_py_file(code_file),
                    code_file,
                    None
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
            except CouldNotHandleEncoding as err:
                messages.append(make_tool_error_message(
                    code_file, 'pep257', 'D000',
                    message='Could not handle the encoding of this file: %s' % err.encoding
                ))
                continue
            except AllError as exc:
                # pep257's Parser.parse_all method raises AllError when an
                # attempt to analyze the __all__ definition has failed.  This
                # occurs when __all__ is too complex to be parsed.
                messages.append(make_tool_error_message(
                    code_file, 'pep257', 'D000',
                    line=1, character=0,
                    message=exc.args[0]
                ))
                continue

        return self.filter_messages(messages)

    def filter_messages(self, messages):
        return [
            message
            for message in messages
            if message.code not in self.ignore_codes
        ]
