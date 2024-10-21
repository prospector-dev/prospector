from abc import ABC, abstractmethod

from prospector.profiles.profile import ProspectorProfile

__all__ = ("Formatter",)

from pathlib import Path
from typing import Any, Optional

from prospector.message import Message


class Formatter(ABC):
    def __init__(
        self,
        summary: dict[str, Any],
        messages: list[Message],
        profile: ProspectorProfile,
        paths_relative_to: Optional[Path] = None,
    ) -> None:
        self.summary = summary
        self.messages = messages
        self.profile = profile
        self.paths_relative_to = paths_relative_to

    @abstractmethod
    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        raise NotImplementedError

    def _make_path(self, path: Path) -> str:
        if self.paths_relative_to is None:
            path = path.absolute()
        elif path.is_absolute():
            path = path.relative_to(self.paths_relative_to)
        return str(path)

    def _message_to_dict(self, message: Message) -> dict[str, Any]:
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
