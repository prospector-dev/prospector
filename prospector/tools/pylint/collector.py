from __future__ import absolute_import
from pylint.reporters import BaseReporter


class Collector(BaseReporter):

    name = 'collector'

    def __init__(self, output=None):
        BaseReporter.__init__(self, output=output)
        self._messages = []

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
        pass

    def get_messages(self):
        return self._messages
