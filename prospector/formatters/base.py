
__all__ = (
    'Formatter',
)


# pylint: disable=R0903
class Formatter(object):
    def __init__(self, summary, messages):
        self.summary = summary
        self.messages = messages

    def render(self, summary=True, messages=True):
        pass
