from __future__ import absolute_import
import json
from pylint.reporters import BaseReporter


class JsonFormatter(BaseReporter):

    def __init__(self, output=None, indent=2):
        BaseReporter.__init__(self, output=output)
        self._messages = []
        self.indent = indent

    def add_message(self, msg_id, location, msg):
        location = {
            'path': location[0],
            'module': location[1],
            'function': location[2],
            'line': location[3],
            'character': location[4]
        }

        message = {
            'msg_id': msg_id,
            'location': location,
            'message': msg
        }

        self._messages.append(message)

    def _display(self, layout):
        print json.dumps(self._messages, indent=self.indent)

    @classmethod
    def get_reporter_class(cls):
        return '%s.%s' % (cls.__module__, cls.__name__)