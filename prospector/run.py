import sys
from pylint.lint import Run
from prospector.linter import ProspectorLinter


def run():
    run_helper = Run
    run_helper.LinterClass = ProspectorLinter

    # note: Pylint will exit with a status code indicating the health of the
    # code it was checking. Prospector will not mimic this behaviour, as it
    # interferes with scripts which depend on and expect the exit code of the
    # code checker to match whether the check itself was successful
    # TODO: add a command line argument to re-enable the exit code behaviour of pylint
    run_helper(sys.argv[1:], exit=False)
    sys.exit(0)


if __name__ == '__main__':
    run()