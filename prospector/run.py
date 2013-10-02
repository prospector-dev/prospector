import sys
import argparse
from pylint.lint import Run
from prospector.formatters.json import JsonFormatter
from prospector.linter import ProspectorLinter


_PROFILE_PLUGIN_MAP = {
    'celery': 'pylint_celery',
    'django': 'pylint_django',
}

_FORMATTERS = {
    'json': JsonFormatter.get_reporter_class(),
    'text': JsonFormatter.get_reporter_class()
}

def make_arg_parser():
    parser = argparse.ArgumentParser(description="Performs analysis of Python code")

    profile_help = 'A list of one or more profiles to use.'
    parser.add_argument('-p', '--profiles', action='append', help=profile_help)
    parser.add_argument('-f', '--format', default='text',
                        help="The output format. Valid values are text, json (default: text)")

    parser.add_argument('paths', nargs='+', help="The path(s) to the python packages or modules to inspect")

    return parser


def run():
    parser = make_arg_parser()
    args = parser.parse_args()

    run_helper = Run
    run_helper.LinterClass = ProspectorLinter

    pylint_args = ['--max-line-length=160',
                   '--output-format=%s' % _FORMATTERS[args.format]]

    if args.profiles:
        plugins = ','.join([_PROFILE_PLUGIN_MAP.get(profile, profile) for profile in args.profiles])
        pylint_args.append('--load-plugins=%s' % plugins)

    pylint_args.append(' '.join(args.paths))

    # note: Pylint will exit with a status code indicating the health of the
    # code it was checking. Prospector will not mimic this behaviour, as it
    # interferes with scripts which depend on and expect the exit code of the
    # code checker to match whether the check itself was successful
    # TODO: add a command line argument to re-enable the exit code behaviour of pylint
    run_helper(pylint_args, exit=False)
    sys.exit(0)


if __name__ == '__main__':
    run()