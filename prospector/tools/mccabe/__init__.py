from __future__ import absolute_import

import ast
import os.path

from mccabe import PathGraphingAstVisitor

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'McCabeTool',
)


def _find_code_files(rootpath, ignores):
    code_files = []

    for root, _, files in os.walk(rootpath):
        for potential in files:
            fullpath = os.path.relpath(os.path.join(root, potential), rootpath)
            if potential.endswith('.py') and not any([ip.search(fullpath) for ip in ignores]):
                code_files.append(fullpath)

    return code_files


class McCabeTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(McCabeTool, self).__init__(*args, **kwargs)
        self._code_files = []
        self.ignore_codes = ()
        self.max_complexity = 10

    def prepare(self, rootpath, ignore, args, adaptors):
        self._code_files = _find_code_files(rootpath, ignore)

        for adaptor in adaptors:
            adaptor.adapt_mccabe(self)

    def run(self):
        messages = []

        for code_file in self._code_files:
            try:
                tree = ast.parse(
                    open(code_file, 'r').read(),
                    filename=code_file,
                )
            except (SyntaxError, TypeError):
                location = Location(
                    path=code_file,
                    module=None,
                    function=None,
                    line=1,
                    character=0,
                )
                message = Message(
                    source='mccabe',
                    code='MC0000',
                    location=location,
                    message='Could not parse file',
                )
                messages.append(message)
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
