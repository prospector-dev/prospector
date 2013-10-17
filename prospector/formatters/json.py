from __future__ import absolute_import
import json
from prospector.formatters.base import FormatterBase


class JsonFormatter(FormatterBase):

    def __init__(self, indent=2):
        self.indent = indent

    def format_messages(self, messages):
        print json.dumps(messages, indent=self.indent)
