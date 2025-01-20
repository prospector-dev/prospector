from abc import ABC, abstractmethod

from prospector.profiles.profile import ProspectorProfile

__all__ = ("Formatter",)

from pathlib import Path
from typing import Any, Optional

from prospector.message import Location, Message


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

    def _make_path(self, location: Location) -> Path:
        path_ = location.relative_path(self.paths_relative_to)
        return Path() if path_ is None else path_

    def _message_to_dict(self, message: Message) -> dict[str, Any]:
        loc = {
            "path": str(self._make_path(message.location)),
            "module": message.location.module,
            "function": message.location.function,
            "line": message.location.line,
            "character": message.location.character,
        }
        if message.location.line_end is not None and message.location.line_end != -1:
            loc["lineEnd"] = message.location.line_end
        if message.location.character_end is not None and message.location.character_end != -1:
            loc["characterEnd"] = message.location.character_end
        result = {
            "source": message.source,
            "code": message.code,
            "location": loc,
            "message": message.message,
            "isFixable": message.is_fixable,
        }
        if message.doc_url:
            result["docUrl"] = message.doc_url

        return result
