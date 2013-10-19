

# This class is only referenced once, causing warning R0922, however it will be used
# more in the future as additional tools are added to Prospector
class ToolBase(object):  # pylint: disable=R0922

    def prepare(self, rootpath, args, adaptors):
        pass

    def run(self):
        raise NotImplementedError
