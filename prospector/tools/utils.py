import sys


class CaptureStream:
    def __init__(self):
        self.contents = ""

    def write(self, text):
        self.contents += text

    def close(self):
        pass

    def flush(self):
        pass


class CaptureOutput:
    def __init__(self, hide):
        self.hide = hide
        self._prev_streams = None
        self.stdout, self.stderr = None, None

    def __enter__(self):
        if self.hide:
            self._prev_streams = [
                sys.stdout,
                sys.stderr,
                sys.__stdout__,
                sys.__stderr__,
            ]
            self.stdout = CaptureStream()
            self.stderr = CaptureStream()
            sys.stdout, sys.__stdout__ = self.stdout, self.stdout  # type: ignore[misc]
            sys.stderr, sys.__stderr__ = self.stderr, self.stderr  # type: ignore[misc]
        return self

    def get_hidden_stdout(self):
        return self.stdout.contents

    def get_hidden_stderr(self):
        return self.stderr.contents

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hide:
            sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__ = self._prev_streams  # type: ignore[misc]
            del self._prev_streams
