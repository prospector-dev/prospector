from pathlib import Path
from typing import Optional, Union


class Location:
    def __init__(
        self, path: Union[Path, str], module: Optional[str], function: Optional[str], line: int, character: int
    ):
        if isinstance(path, Path):
            self._path = path
        elif isinstance(path, str):
            self._path = Path(path)
        else:
            raise ValueError
        self.module = module or None
        self.function = function or None
        self.line = None if line == -1 else line
        self.character = None if character == -1 else character

    @property
    def path(self):
        return self._path

    def absolute_path(self) -> Path:
        return self._path.absolute()

    def relative_path(self, root: Path) -> Path:
        return self._path.relative_to(root)

    def __repr__(self) -> str:
        return f"{self._path}:L{self.line}:{self.character}"

    def __hash__(self) -> int:
        return hash((self._path, self.line, self.character))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self._path == other._path and self.line == other.line and self.character == other.character

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Location):
            raise ValueError
        if self._path == other._path:
            if self.line == other.line:
                return (self.character or -1) < (other.character or -1)
            return (self.line or -1) < (other.line or -1)  # line can be None if it's a file-global warning
        return self._path < other._path


class Message:
    def __init__(self, source: str, code: str, location: Location, message: str):
        self.source = source
        self.code = code
        self.location = location
        self.message = message

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
    filepath: Union[Path, str],
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
