

class ToolBase(object):

    def prepare(self, ignores, rootpath, args, adaptors):
        pass

    def run(self):
        raise NotImplementedError
