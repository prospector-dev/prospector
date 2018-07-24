# -*- coding: utf-8 -*-
import os

from prospector.suppression import get_suppressions


def filter_messages(relative_filepaths, root, messages):
    """
    This method post-processes all messages output by all tools, in order to filter
    out any based on the overall output.

    The main aim currently is to use information about messages suppressed by
    pylint due to inline comments, and use that to suppress messages from other
    tools representing the same problem.

    For example:

        import banana  # pylint:disable=unused-import

    In this situation, pylint will not warn about an unused import as there is
    inline configuration to disable the warning. Pyflakes will still raise that
    error, however, because it does not understand pylint disabling messages.
    This method uses the information about suppressed messages from pylint to
    squash the unwanted redundant error from pyflakes and frosted.
    """
    paths_to_ignore, lines_to_ignore, messages_to_ignore = get_suppressions(relative_filepaths, root, messages)

    filtered = []
    for message in messages:
        # first get rid of the pylint informational messages
        relative_message_path = os.path.relpath(message.location.path)

        if message.source == 'pylint' and message.code in ('suppressed-message', 'file-ignored',):
            continue

        # some files are skipped entirely by messages
        if relative_message_path in paths_to_ignore:
            continue

        # some lines are skipped entirely by messages
        if relative_message_path in lines_to_ignore:
            if message.location.line in lines_to_ignore[relative_message_path]:
                continue

        # and some lines have only certain messages explicitly ignored
        if relative_message_path in messages_to_ignore:
            if message.location.line in messages_to_ignore[relative_message_path]:
                if message.code in messages_to_ignore[relative_message_path][message.location.line]:
                    continue

        # otherwise this message was not filtered
        filtered.append(message)

    return filtered
