from abc import ABC, abstractmethod

__all__ = ("Formatter",)


class Formatter(ABC):
    def __init__(self, summary, messages, profile):
        self.summary = summary
        self.messages = messages
        self.profile = profile

    @abstractmethod
    def render(self, summary=True, messages=True, profile=False):
        raise NotImplementedError
