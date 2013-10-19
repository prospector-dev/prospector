from prospector.adaptor.base import AdaptorBase


class NoDocWarningsAdaptor(AdaptorBase):
    name = 'no-doc-warnings'

    def adapt_pylint(self, linter):
        linter.disable('C0112')
        linter.disable('C0111')
