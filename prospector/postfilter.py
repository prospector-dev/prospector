from collections import defaultdict
import re


_I0020_REGEXP = re.compile(r'^Suppressed \'([a-z0-9-]+)\' \(from line \d+\)$')

_SUPPRESS_IF = {
    'pyflakes': {
        'FL0001': ('unused-import',)
    },
    'frosted': {
        'E101': ('unused-import',)
    }
}



def _get_pylint_informational(messages):
    remainder = []
    informational = defaultdict(lambda: defaultdict(list))
    for message in messages:
        if message.source == 'pylint' and message.code.startswith('I'):
            if message.code == 'I0020':
                # this is a message indicating that a message was raised
                # by pylint but suppressed by configuration in the file
                match = _I0020_REGEXP.match(message.message)
                suppressed_code = match.group(1)
                line_dict = informational[message.location.path]
                line_dict[message.location.line].append(suppressed_code)
        else:
            remainder.append(message)
    return informational, remainder


def filter_messages(messages):
    """
    This method post-processes all messages output by all tools, in order to filter
    out any based on the overall output.

    The main aim currently is to use information about messages suppressed by
    pylint due to inline comments, and use that to suppress messages from other
    tools representing the same problem.

    For example:

        import banana  # pylint:disable=W0611

    In this situation, pylint will not warn about an unused import as there is
    inline configuration to disable the warning. Pyflakes will still raise that
    error, however, because it does not understand pylint disabling messages.
    This method uses the information about suppressed messages from pylint to
    squash the unwanted redundant error from pyflakes and frosted.
    """
    informational, messages = _get_pylint_informational(messages)

    filtered = []
    for message in messages:
        # if this message is not one which we may supress, we can skip the next steps
        suppress_if = _SUPPRESS_IF.get(message.source, {}).get(message.code, None)
        if suppress_if is None or message.location.path not in informational:
            filtered.append(message)
            continue

        # figure out if there's anything on the same line
        info = informational.get(message.location.path, {}).get(message.location.line, None)
        if info is None:
            filtered.append(message)
            continue

        # now figure out if any of the information on this line is suppressing
        # this current message
        for supress_code in info:
            if supress_code in suppress_if:
                # this means that a message was suppressed with a code which
                # matches the current message's purpose - eg, pylint has
                # suppressed an 'unused-import', and this message also represents
                # an unused import, so should be supressed too
                break
        else:
            filtered.append(message)

    return filtered