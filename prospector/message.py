from pathlib import Path
from typing import Optional, Union


class Location:
    _path: Optional[Path]

    def __init__(
        self,
        path: Optional[Union[Path, str]],
        module: Optional[str],
        function: Optional[str],
        line: Optional[int],
        character: Optional[int],
        line_end: Optional[int] = None,
        character_end: Optional[int] = None,
    ):
        if isinstance(path, Path):
            self._path = path.absolute()
        elif isinstance(path, str):
            self._path = Path(path).absolute()
        elif path is None:
            self._path = None
        else:
            raise ValueError
        self.module = module or None
        self.function = function or None
        self.line = None if line == -1 else line
        self.character = None if character == -1 else character
        self.line_end = line_end
        self.character_end = character_end

    @property
    def path(self) -> Optional[Path]:
        return self._path

    def absolute_path(self) -> Optional[Path]:
        return self._path

    def relative_path(self, root: Optional[Path]) -> Optional[Path]:
        if self._path is None:
            return None
        if root is None:
            return self._path
        return self._path.relative_to(root) if self._path.is_relative_to(root) else self._path

    def __repr__(self) -> str:
        return f"{self._path}:L{self.line}:{self.character}"

    def __hash__(self) -> int:
        return hash((self._path, self.line, self.character))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return False
        return self._path == other._path and self.line == other.line and self.character == other.character

    def __lt__(self, other: "Location") -> bool:
        if not isinstance(other, Location):
            raise ValueError

        if self._path is None and other._path is None:
            return False
        if self._path is None:
            return True
        if other._path is None:
            return False
        if self._path == other._path:
            if self.line == other.line:
                return (self.character or -1) < (other.character or -1)
            return (self.line or -1) < (other.line or -1)  # line can be None if it's a file-global warning
        return self._path < other._path


class Message:
    def __init__(
        self,
        source: str,
        code: str,
        location: Location,
        message: str,
        doc_url: Optional[str] = None,
        is_fixable: bool = False,
    ):
        self.source = source
        self.code = code
        self.location = location
        self.message = message
        self.doc_url = doc_url
        self.is_fixable = is_fixable

    def __repr__(self) -> str:
        return f"{self.source}-{self.code}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return False
        if self.location == other.location:
            return self.code == other.code
        return False

    def __lt__(self, other: "Message") -> bool:
        if self.location == other.location:
            return self.code < other.code
        return self.location < other.location


def make_tool_error_message(
    filepath: Union[Path, str],
    source: str,
    code: str,
    message: str,
    line: Optional[int] = None,
    character: Optional[int] = None,
    module: Optional[str] = None,
    function: Optional[str] = None,
) -> Message:
    location = Location(path=filepath, module=module, function=function, line=line, character=character)
    return Message(source=source, code=code, location=location, message=message)
