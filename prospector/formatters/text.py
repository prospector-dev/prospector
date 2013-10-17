from prospector.formatters.base import FormatterBase
import sys


TEMPLATE = """%(module)s (%(path)s):
    L%(line)s:%(character)s %(function)s: %(source)s - %(code)s
    %(message)s
"""


class TextFormatter(FormatterBase):

    def format(self, messages):
        for message in messages:
            info = {}
            info.update(message.as_dict())
            del info['location']
            info.update(message.location.as_dict())
            line = TEMPLATE % info
            sys.stdout.write(line)
            sys.stdout.write('\n')
