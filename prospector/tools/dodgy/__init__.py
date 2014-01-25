from __future__ import absolute_import

from dodgy.run import run_checks
import os
import re
from prospector.message import Location, Message
from prospector.tools.base import ToolBase


def module_from_path(path):
    # note : assumes a relative path
    module = re.sub(r'\.py', '', path)
    return '.'.join(module.split(os.path.sep)[1:])


class DodgyTool(ToolBase):

    def prepare(self, rootpath, ignore, args, adaptors):
        self.rootpath = rootpath
        self.ignore = ignore

    def run(self):
        warnings = run_checks(self.rootpath, self.ignore)
        messages = []

        for warning in warnings:
            path = warning['path']
            loc = Location(path, module_from_path(path), '', warning['line'], 0, absolute_path=False)
            msg = Message('dodgy', warning['code'], loc, warning['message'])
            messages.append(msg)

        return messages
