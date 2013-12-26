import sys

_SUMMARY_TEMPLATE = """Started: %(started)s
Finished: %(completed)s
Time taken: %(time_taken)s seconds
Formatter: %(formatter)s
Strictness: %(strictness)s
Libraries Used: %(libraries)s
Tools run: %(tools)s
Adaptors: %(adaptors)s
Messages Found: %(message_count)d
"""


_MESSAGE_TEMPLATE = """%(module)s %(path)s:
    L%(line)s:%(character)s %(function)s: %(source)s - %(code)s
    %(message)s
"""


def format_messages(summary, messages):
    if summary is not None:
        sys.stdout.write("Check Information\n=================\n")
        sys.stdout.write(_SUMMARY_TEMPLATE % summary)
        sys.stdout.write('\n\n')

    if messages is not None:
        sys.stdout.write("Messages\n========\n\n")
        for message in messages:
            info = {}
            info.update(message.as_dict())
            del info['location']
            info.update(message.location.as_dict())
            if info['module'] is None:
                info['module'] = info['path']
                info['path'] = ''
            else:
                info['path'] = '(%s)' % info['path']

            if info['line'] is None:
                info['line'] = '-'
                info['character'] = '-'
            line = _MESSAGE_TEMPLATE % info
            sys.stdout.write(line)
            sys.stdout.write('\n')
