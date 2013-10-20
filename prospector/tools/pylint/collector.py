from __future__ import absolute_import
from pylint.reporters import BaseReporter
from prospector.message import Location, Message


class Collector(BaseReporter):

    name = 'collector'

    def __init__(self):
        BaseReporter.__init__(self, output=None)
        self._messages = []

    def add_message(self, msg_id, location, msg):
        # (* magic is acceptable here)
        # pylint: disable=W0142
        loc = Location(*location)
        message = Message('pylint', msg_id, loc, msg)
        self._messages.append(message)

    def _display(self, layout):
        pass

    def get_messages(self):
        return self._messages
