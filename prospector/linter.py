from pylint.lint import PyLinter


class ProspectorLinter(PyLinter): # pylint: disable=R0901,R0904

    def __init__(self, *args, **kwargs):
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)
        # do some additional things!
