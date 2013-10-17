from prospector.profiles.base import ProspectorProfile


class CeleryProfile(ProspectorProfile):

    def apply_to_pylint(self, linter):
        linter.load_plugin_modules(['pylint_celery'])
