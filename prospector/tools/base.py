

class ToolBase(object):

    def prepare(self, found_files, args, adaptors):
        pass

    def run(self):
        raise NotImplementedError
