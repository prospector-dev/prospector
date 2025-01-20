from io import StringIO

from pylint.exceptions import UnknownMessageError
from pylint.message import Message as PylintMessage
from pylint.message import MessageDefinitionStore
from pylint.reporters import BaseReporter

from prospector.message import Location, Message


class Collector(BaseReporter):
    name = "collector"

    def __init__(self, message_store: MessageDefinitionStore) -> None:
        BaseReporter.__init__(self, output=StringIO())
        self._message_store = message_store
        self._messages: list[Message] = []

    def handle_message(self, msg: PylintMessage) -> None:
        loc = Location(msg.abspath, msg.module, msg.obj, msg.line, msg.column, msg.end_line, msg.end_column)

        # At this point pylint will give us the code but we want the
        # more user-friendly symbol
        try:
            msg_data = self._message_store.get_message_definitions(msg.msg_id)
        except UnknownMessageError:
            # this shouldn't happen, as all pylint errors should be
            # in the message store, but just in case we'll fall back
            # to using the code.
            msg_symbol = msg.msg_id
        else:
            msg_symbol = msg_data[0].symbol

        message = Message(
            "pylint",
            msg_symbol,
            loc,
            msg.msg,
            doc_url=f"https://pylint.readthedocs.io/en/latest/user_guide/messages/{msg.category}/{msg.symbol}.html",
        )
        self._messages.append(message)

    def get_messages(self) -> list[Message]:
        return self._messages
