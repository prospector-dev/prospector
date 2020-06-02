# -*- coding: utf-8 -*-

# We are trying to handle pylint changes in their exception classes


class FatalProspectorException(Exception):

    """
    Exception used to indicate an internal prospector problem.
    Problems in prospector itself should raise this to notify
    the user directly. Errors in dependent tools which should
    be squashed and the user notified elegantly.
    """

    def __init__(self, message):
        self.message = message
