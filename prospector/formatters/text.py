from pylint.reporters import BaseReporter


TEMPLATE = """%(module)s (%(path)s):
    L%(line)s:%(character)s %(function)s: %(msg_id)s
    %(message)s
"""


class TextFormatter(BaseReporter):

    name = 'text'

    def __init__(self, output=None):
        BaseReporter.__init__(self, output=output)
        self._messages = []

    def add_message(self, msg_id, location, msg):

        info = {
            'path': location[0],
            'module': location[1],
            'function': location[2],
            'line': location[3],
            'character': location[4] if location[4] != '-1' else '',
            'msg_id': msg_id,
            'message': msg
        }

        self.writeln(TEMPLATE % info)

    def _display(self, layout):
        pass

    @classmethod
    def get_reporter_class(cls):
        return '%s.%s' % (cls.__module__, cls.__name__)
