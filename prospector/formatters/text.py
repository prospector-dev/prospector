from prospector.formatters.base import FormatterBase
import sys


TEMPLATE = """%(module)s (%(path)s):
    L%(line)s:%(character)s %(function)s: %(msg_id)s
    %(message)s
"""


class TextFormatter(FormatterBase):

    def format_messages(self, messages):
        for message in messages:
            info = {}
            info.update(message)
            del info['location']
            info.update(message['location'])
            line = TEMPLATE % info
            sys.stdout.write(line)
            sys.stdout.write('\n')
