


def import_plugin(plugin_name):
    return lambda linter: linter.load_plugin_modules([plugin_name])


def no_doc_warnings(linter):
    linter.disable('C0112')
    linter.disable('C0111')


PROFILES = {
    'no_doc_warnings': no_doc_warnings,
    # frameworks:
    'celery': import_plugin('pylint_celery'),
    'django': import_plugin('pylint_django')
}
