from pylint.lint import PyLinter


class ProspectorLinter(PyLinter):

    def __init__(self, *args, **kwargs):
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)
        # do some additional things!

    def _load_default_plugins(self):
        # We want to manually choose which checkers and reporters
        # are used rather than assume the defaults. In this Linter
        # class, they will be loaded through the same mechanism
        # as additional plugins.
        pass