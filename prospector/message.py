

class Location(object):

    def __init__(self, path, module, function, line, character):
        self.path = path
        self.module = module
        self.function = function
        self.line = line
        self.character = character

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

    def as_dict(self):
        return {
            'source': self.source,
            'code': self.code,
            'location': self.location.as_dict(),
            'message': self.message
        }