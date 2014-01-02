

class ToolBase(object):

    def prepare(self, rootpath, ignore, args, adaptors):
        pass

    def run(self):
        raise NotImplementedError
