# -*- coding: utf-8 -*-
from __future__ import absolute_import

import ast
from mccabe import PathGraphingAstVisitor
from prospector.encoding import read_py_file, CouldNotHandleEncoding

from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase


__all__ = (
    'McCabeTool',
)


class McCabeTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(McCabeTool, self).__init__(*args, **kwargs)
        self.ignore_codes = ()
        self.max_complexity = 10

    def configure(self, prospector_config, _):
        self.ignore_codes = prospector_config.get_disabled_messages('mccabe')

        options = prospector_config.tool_options('mccabe')
        if 'max-complexity' in options:
            self.max_complexity = options['max-complexity']

    def run(self, found_files):
        messages = []

        for code_file in found_files.iter_module_paths():
            try:
                contents = read_py_file(code_file)
                tree = ast.parse(
                    contents,
                    filename=code_file,
                )
            except CouldNotHandleEncoding as err:
                messages.append(make_tool_error_message(
                    code_file, 'mccabe', 'MC0000',
                    message='Could not handle the encoding of this file: %s' % err.encoding
                ))
                continue
            except SyntaxError as err:
                messages.append(make_tool_error_message(
                    code_file, 'mccabe', 'MC0000',
                    line=err.lineno, character=err.offset,
                    message='Syntax Error'
                ))
                continue
            except TypeError:
                messages.append(make_tool_error_message(
                    code_file, 'mccabe', 'MC0000',
                    message='Unable to parse file'
                ))
                continue

            visitor = PathGraphingAstVisitor()
            visitor.preorder(tree, visitor)

            for graph in visitor.graphs.values():
                complexity = graph.complexity()
                if complexity > self.max_complexity:
                    location = Location(
                        path=code_file,
                        module=None,
                        function=graph.entity,
                        line=graph.lineno,
                        character=0,
                        absolute_path=True
                    )
                    message = Message(
                        source='mccabe',
                        code='MC0001',
                        location=location,
                        message='%s is too complex (%s)' % (
                            graph.entity,
                            complexity,
                        ),
                    )
                    messages.append(message)

        return self.filter_messages(messages)

    def filter_messages(self, messages):
        return [
            message
            for message in messages
            if message.code not in self.ignore_codes
        ]
