
class ToolBase(object):

    def prepare(self, rootpath, args, profiles):
        pass

    def run(self):
        raise NotImplementedError
