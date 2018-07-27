# -*- coding: utf-8 -*-
from __future__ import absolute_import

from prospector.exceptions import UnknownMessageError
from prospector.message import Location, Message
from pylint.__pkginfo__ import numversion as PYLINT_VERSION
from pylint.reporters import BaseReporter


class Collector(BaseReporter):

    name = 'collector'

    def __init__(self, message_store):
        BaseReporter.__init__(self, output=None)
        self._message_store = message_store
        self._messages = []

    def handle_message(self, msg):
        location = (msg.abspath, msg.module, msg.obj, msg.line, msg.column)
        self.add_message(msg.msg_id, location, msg.msg)

    def add_message(self, msg_id, location, msg):
        # (* magic is acceptable here)
        loc = Location(*location)
        # At this point pylint will give us the code but we want the
        # more user-friendly symbol
        try:
            if PYLINT_VERSION < (2, 0):
                msg_data = self._message_store.check_message_id(msg_id)
            else:
                msg_data = self._message_store.get_message_definition(msg_id)
        except UnknownMessageError:
            # this shouldn't happen, as all pylint errors should be
            # in the message store, but just in case we'll fall back
            # to using the code.
            msg_symbol = msg_id
        else:
            msg_symbol = msg_data.symbol

        message = Message('pylint', msg_symbol, loc, msg)
        self._messages.append(message)

    def _display(self, layout):
        pass

    def get_messages(self):
        return self._messages
