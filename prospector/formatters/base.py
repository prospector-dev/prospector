from abc import ABC, abstractmethod

__all__ = ("Formatter",)

from pathlib import Path

from prospector.message import Message


class Formatter(ABC):
    def __init__(self, summary, messages, profile):
        self.summary = summary
        self.messages = messages
        self.profile = profile

    @abstractmethod
    def render(self, summary=True, messages=True, profile=False, paths_relative_to: Path = None):
        raise NotImplementedError

    def _message_to_dict(self, message: Message, relative_to: Path = None) -> dict:
        if relative_to is None:
            path = message.location.absolute_path()
        else:
            path = message.location.relative_path(relative_to)
        path = str(path)

        loc = {
            "path": path,
            "module": message.location.module,
            "function": message.location.function,
            "line": message.location.line,
            "character": message.location.character,
        }
        return {
            "source": message.source,
            "code": message.code,
            "location": loc,
            "message": message.message,
        }
