
class AdaptorBase(object):

    def adapt_pylint(self, linter):
        pass

    def adapt_mccabe(self, tool):
        pass

    def adapt_pyflakes(self, tool):
        pass

    def adapt_frosted(self, tool):
        pass

    def adapt_pep8(self, style_guide, use_config=True):
        pass
