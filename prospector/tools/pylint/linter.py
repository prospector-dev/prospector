from logilab.common.configuration import OptionsManagerMixIn
from pylint.lint import PyLinter


class ProspectorLinter(PyLinter):  # pylint: disable=R0901,R0904

    def __init__(self, *args, **kwargs):
        # set up the standard PyLint linter
        PyLinter.__init__(self, *args, **kwargs)

        # do some additional things!

        # for example, we want to re-initialise the OptionsManagerMixin
        # to supress the config error warning
        OptionsManagerMixIn.__init__(self, usage=PyLinter.__doc__, quiet=True)
