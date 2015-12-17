# -*- coding: utf-8 -*-
import sys


class CaptureStream(object):
    def __init__(self):
        self.contents = ''

    def write(self, text):
        self.contents += text

    def close(self):
        pass

    def flush(self):
        pass


# The class name here is lowercase as it is a context manager, which
# typically tend to me lowercase.
class capture_output(object):  # noqa pylint:disable=invalid-name

    def __init__(self, hide):
        self.hide = hide

    def __enter__(self):
        if self.hide:
            self._prev_streams = [sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__]
            self.stdout = CaptureStream()
            self.stderr = CaptureStream()
            sys.stdout, sys.__stdout__ = self.stdout, self.stdout
            sys.stderr, sys.__stderr__ = self.stderr, self.stderr
        return self

    def get_hidden_stdout(self):
        return self.stdout.contents

    def get_hidden_stderr(self):
        return self.stderr.contents

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hide:
            sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__ = self._prev_streams
            del self._prev_streams
