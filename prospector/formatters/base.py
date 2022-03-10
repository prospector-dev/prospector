from abc import ABC, abstractmethod

__all__ = ("Formatter",)

from pathlib import Path

from prospector.message import Message


class Formatter(ABC):
    def __init__(self, summary, messages, profile, paths_relative_to: Path = None):
        self.summary = summary
        self.messages = messages
        self.profile = profile
        self.paths_relative_to = paths_relative_to

    @abstractmethod
    def render(self, summary=True, messages=True, profile=False):
        raise NotImplementedError

    def _make_path(self, path: Path) -> str:
        if self.paths_relative_to is None:
            path = path.absolute()
        elif path.is_absolute():
            path = path.relative_to(self.paths_relative_to)
        return str(path)

    def _message_to_dict(self, message: Message) -> dict:
        loc = {
            "path": self._make_path(message.location.path),
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
