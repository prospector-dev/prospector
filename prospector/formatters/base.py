
__all__ = (
    'Formatter',
)


# pylint: disable=R0903
class Formatter(object):
    def __init__(self, summary, messages, profile):
        self.summary = summary
        self.messages = messages
        self.profile = profile

    def render(self, summary=True, messages=True, profile=False):
        pass
