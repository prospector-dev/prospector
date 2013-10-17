from prospector.profiles.base import ProspectorProfile


class NoDocWarningsProfile(ProspectorProfile):

    def apply_to_pylint(self, linter):
        linter.disable('C0112')
        linter.disable('C0111')
