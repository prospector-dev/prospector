from prospector.adaptor import AdaptorBase


class NoOpAdaptor(AdaptorBase):
    name = 'no-op'
    # placeholder for strictness adaptors for now
    def adapt_pylint(self, linter):
        pass