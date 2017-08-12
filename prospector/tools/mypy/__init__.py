# -*- coding: utf-8 -*-
from __future__ import absolute_import

from mypy import api

from prospector.tools import ToolBase


__all__ = (
    'MypyTool',
)


class MypyTool(ToolBase):

    def __init__(self, *args, **kwargs):
        super(MypyTool, self).__init__(*args, **kwargs)
        self.checker = api

    def run(self, found_files):
        import pdb ; pdb.set_trace()
        mypy = self.checker.run(found_files)