# -*- coding: utf-8 -*-
import os


class Location(object):
    def __init__(self, path, module, function, line, character, absolute_path=True):
        self.path = path
        self._path_is_absolute = absolute_path
        self.module = module or None
        self.function = function or None
        self.line = None if line == -1 else line
        self.character = None if character == -1 else character

    def to_absolute_path(self, root):
        if self._path_is_absolute:
            return
        self.path = os.path.abspath(os.path.join(root, self.path))
        self._path_is_absolute = True

    def to_relative_path(self, root):
        if not self._path_is_absolute:
            return
        self.path = os.path.relpath(self.path, root)
        self._path_is_absolute = False

    def as_dict(self):
        return {
            "path": self.path,
            "module": self.module,
            "function": self.function,
            "line": self.line,
            "character": self.character,
        }

    def __hash__(self):
        return hash((self.path, self.line, self.character))

    def __eq__(self, other):
        return self.path == other.path and self.line == other.line and self.character == other.character

    def __lt__(self, other):
        if self.path == other.path:
            if self.line == other.line:
                return (self.character or -1) < (other.character or -1)
            return (self.line or -1) < (other.line or -1)  # line can be None if it a file-global warning
        return self.path < other.path


class Message(object):
    def __init__(self, source, code, location, message):
        self.source = source
        self.code = code
        self.location = location
        self.message = message

    def to_absolute_path(self, root):
        self.location.to_absolute_path(root)

    def to_relative_path(self, root):
        self.location.to_relative_path(root)

    def as_dict(self):
        return {
            "source": self.source,
            "code": self.code,
            "location": self.location.as_dict(),
            "message": self.message,
        }

    def __repr__(self):
        return "%s-%s" % (self.source, self.code)

    def __eq__(self, other):
        if self.location == other.location:
            return self.code == other.code
        else:
            return False

    def __lt__(self, other):
        if self.location == other.location:
            return self.code < other.code
        return self.location < other.location


def make_tool_error_message(filepath, source, code, message, line=0, character=0, module=None, function=None):
    location = Location(path=filepath, module=module, function=function, line=line, character=character)
    return Message(source=source, code=code, location=location, message=message)
