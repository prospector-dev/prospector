import sys
from io import TextIOWrapper
from typing import Optional


class CaptureStream(TextIOWrapper):
    def __init__(self, tty: bool) -> None:
        self.contents = ""
        self._tty = tty

    def write(self, text: str, /) -> int:
        self.contents += text
        return len(text)

    def close(self) -> None:
        pass

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return self._tty


class CaptureOutput:
    _prev_streams = None
    stdout: Optional[CaptureStream] = None
    stderr: Optional[CaptureStream] = None

    def __init__(self, hide: bool) -> None:
        self.hide = hide

    def __enter__(self) -> "CaptureOutput":
        if self.hide:
            is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

            self._prev_streams = (
                sys.stdout,
                sys.stderr,
                sys.__stdout__,
                sys.__stderr__,
            )
            self.stdout = CaptureStream(is_a_tty)
            self.stderr = CaptureStream(is_a_tty)
            sys.stdout, sys.__stdout__ = self.stdout, self.stdout  # type: ignore[misc]
            sys.stderr, sys.__stderr__ = self.stderr, self.stderr  # type: ignore[misc]
        return self

    def get_hidden_stdout(self) -> str:
        return "" if self.stdout is None else self.stdout.contents

    def get_hidden_stderr(self) -> str:
        return "" if self.stderr is None else self.stderr.contents

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: type) -> None:
        if self.hide:
            assert self._prev_streams is not None
            sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__ = self._prev_streams  # type: ignore[misc]
            del self._prev_streams
