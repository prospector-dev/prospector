# -*- coding: utf-8 -*-
try:
    from pylint.utils import UnknownMessage as UnknownMessageError
except ImportError:
    from pylint.exceptions import UnknownMessageError

class FatalProspectorException(Exception):

    """
    Exception used to indicate an internal prospector problem.
    Problems in prospector itself should raise this to notify
    the user directly. Errors in dependent tools which should
    be squashed and the user notified elegantly.
    """

    def __init__(self, message):
        self.message = message
