# -*- coding: utf-8 -*-
from __future__ import absolute_import
import mimetypes
import os
import re
from dodgy.checks import check_file_contents
from prospector.encoding import read_py_file, CouldNotHandleEncoding
from prospector.message import Location, Message
from prospector.tools.base import ToolBase


def module_from_path(path):
    # note : assumes a relative path
    module = re.sub(r'\.py', '', path)
    return '.'.join(module.split(os.path.sep)[1:])


class DodgyTool(ToolBase):

    def run(self, found_files):

        warnings = []
        for filepath in found_files.iter_file_paths():
            mimetype = mimetypes.guess_type(filepath)
            if mimetype[0] is None or not mimetype[0].startswith('text/') or mimetype[1] is not None:
                continue
            try:
                contents = read_py_file(filepath)
            except CouldNotHandleEncoding:
                continue
            for line, code, message in check_file_contents(contents):
                warnings.append({
                    'line': line, 'code': code, 'message': message,
                    'path': filepath
                })

        messages = []
        for warning in warnings:
            path = warning['path']
            prefix = os.path.commonprefix([found_files.rootpath, path])
            loc = Location(path, module_from_path(path[len(prefix):]), '', warning['line'], 0, absolute_path=True)
            msg = Message('dodgy', warning['code'], loc, warning['message'])
            messages.append(msg)

        return messages
