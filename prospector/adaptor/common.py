from prospector.adaptor.base import AdaptorBase


class CommonAdaptor(AdaptorBase):
    name = 'common-plugin'

    def adapt_pylint(self, linter):
        linter.load_plugin_modules(['pylint_common'])
