import os


class Location(object):

    def __init__(self, path, module, function, line, character):
        self.path = path
        self._path_is_absolute = True
        self.module = module
        self.function = function
        self.line = line
        self.character = character

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
            'path': self.path,
            'module': self.module,
            'function': self.function,
            'line': self.line,
            'character': self.character
        }


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
            'source': self.source,
            'code': self.code,
            'location': self.location.as_dict(),
            'message': self.message
        }
