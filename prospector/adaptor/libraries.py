from prospector.adaptor.base import AdaptorBase


class DjangoAdaptor(AdaptorBase):
    name = 'django'
    ignore_patterns = (
        '(^|/)migrations(/|$)',
    )

    def adapt_pylint(self, linter):
        linter.load_plugin_modules(['pylint_django'])


class CeleryAdaptor(AdaptorBase):
    name = 'celery'

    def adapt_pylint(self, linter):
        linter.load_plugin_modules(['pylint_celery'])
