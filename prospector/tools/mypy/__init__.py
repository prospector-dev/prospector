# -*- coding: utf-8 -*-
from __future__ import absolute_import

from mypy import api

from prospector.message import Location, Message
from prospector.tools import ToolBase


__all__ = (
    'MypyTool',
)


class MypyTool(ToolBase):

    def __init__(self, *args, **kwargs):
        super(MypyTool, self).__init__(*args, **kwargs)
        self.checker = api
        self.options = ['--show-column-numbers']

    def run(self, found_files):
        paths = [path for path in found_files.iter_module_paths()]
        paths.extend(self.options)
        report, err, status = self.checker.run(paths)
        messages = []

        for message in report.splitlines():
            path, line, char, err_type, *err_msg = message.split(':')
            location = Location(
                path=path,
                module=None,
                function=None,
                line=line,
                character=char,
                absolute_path=True
            )
            message = Message(
                source='mypy',
                code=err_type,
                location=location,
                message=''.join(err_msg).strip()
            )
            messages.append(message)

        return messages