from __future__ import absolute_import
import json
from prospector.formatters.base import FormatterBase


class JsonFormatter(FormatterBase):

    def __init__(self, indent=2):
        self.indent = indent

    def format(self, messages):
        output = {'messages': [m.as_dict() for m in messages]}
        print json.dumps(output, indent=self.indent)
