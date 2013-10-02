


def import_plugin(plugin_name):
    def apply(linter):
        linter.load_plugin_modules([plugin_name])
    return apply


def no_doc_warnings(linter):
    linter.disable('C0112')
    linter.disable('C0111')


PROFILES = {
    'no_doc_warnings': no_doc_warnings,
    # frameworks:
    'celery': import_plugin('pylint_celery'),
    'django': import_plugin('pylint_django')
}