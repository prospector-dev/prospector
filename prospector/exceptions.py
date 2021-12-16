class FatalProspectorException(Exception):

    """
    Exception used to indicate an internal prospector problem.
    Problems in prospector itself should raise this to notify
    the user directly. Errors in dependent tools should be
    caught and the user notified elegantly.

    """

    # (see also the --die-on-tool-error flag)

    def __init__(self, message):
        self.message = message
