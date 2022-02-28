import os
from typing import Dict, Optional, Union


class Location:
    def __init__(
        self,
        path: str,
        module: Optional[str],
        function: Optional[str],
        line: int,
        character: int,
        absolute_path: bool = True,
    ):
        self.path = path
        self._path_is_absolute = absolute_path
        self.module = module or None
        self.function = function or None
        self.line = None if line == -1 else line
        self.character = None if character == -1 else character

    def to_absolute_path(self, root: str):  # TODO: use pathlib?
        if self._path_is_absolute:
            return
        self.path = os.path.abspath(os.path.join(root, self.path))
        self._path_is_absolute = True

    def to_relative_path(self, root: str):
        if not self._path_is_absolute:
            return
        self.path = os.path.relpath(self.path, root)
        self._path_is_absolute = False

    def as_dict(self) -> Dict[str, Union[str, int, None]]:
        return {
            "path": self.path,
            "module": self.module,
            "function": self.function,
            "line": self.line,
            "character": self.character,
        }

    def __repr__(self) -> str:
        return f"{self.path}:L{self.line}:{self.character}"

    def __hash__(self) -> int:
        return hash((self.path, self.line, self.character))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self.path == other.path and self.line == other.line and self.character == other.character

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Location):
            raise ValueError
        if self.path == other.path:
            if self.line == other.line:
                return (self.character or -1) < (other.character or -1)
            return (self.line or -1) < (other.line or -1)  # line can be None if it a file-global warning
        return self.path < other.path


class Message:
    def __init__(self, source: str, code: str, location: Location, message: str):
        self.source = source
        self.code = code
        self.location = location
        self.message = message

    def to_absolute_path(self, root: str):
        self.location.to_absolute_path(root)

    def to_relative_path(self, root: str):
        self.location.to_relative_path(root)

    def as_dict(self) -> Dict[str, Union[str, dict]]:
        return {
            "source": self.source,
            "code": self.code,
            "location": self.location.as_dict(),
            "message": self.message,
        }

    def __repr__(self) -> str:
        return "%s-%s" % (self.source, self.code)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return False
        if self.location == other.location:
            return self.code == other.code
        return False

    def __lt__(self, other) -> bool:
        if self.location == other.location:
            return self.code < other.code
        return self.location < other.location


def make_tool_error_message(
    filepath: str,
    source: str,
    code: str,
    message: str,
    line: int = 0,
    character: int = 0,
    module: str = None,
    function: str = None,
) -> Message:
    location = Location(path=filepath, module=module, function=function, line=line, character=character)
    return Message(source=source, code=code, location=location, message=message)
