import sys
import argparse
from logilab.common.textutils import splitstrip
from prospector.profiles import PROFILES
from prospector.formatters.json import JsonFormatter
from prospector.linter import ProspectorLinter



def make_arg_parser():
    parser = argparse.ArgumentParser(description="Performs analysis of Python code")

    profile_help = 'A list of one or more profiles to use.'
    parser.add_argument('-p', '--profiles', action='append', help=profile_help)
    parser.add_argument('-o', '--output-format', default='text',
                        help="The output format. Valid values are 'json', 'text', 'parseable', 'html' (default: text)")

    parser.add_argument('paths', nargs='+', help="The path(s) to the python packages or modules to inspect")

    return parser


def run():
    parser = make_arg_parser()
    args = parser.parse_args()

    linter = ProspectorLinter()
    linter.load_default_plugins()
    linter.register_reporter(JsonFormatter)

    pylint_args = ['--max-line-length=160',
                   '--output-format=%s' % args.output_format]

    if args.output_format not in ('json',):
        # we disable reports for the built-in pylint reporters, but not for
        # the custom ones added by prospector, as it seems that custom reporters
        # get turned off by --reports=no...
        pylint_args.append('--reports=no')

    if args.profiles:
        for profile in args.profiles:
            try:
                PROFILES[profile](linter)
            except KeyError:
                sys.stderr.write("No such profile: %s" % profile)
                sys.exit(2)

    pylint_args.append(' '.join(args.paths))

    # this rather cryptic invocation is lifted from the Pylint Run class
    linter.read_config_file()
    # is there some additional plugins in the file configuration, in
    config_parser = linter.cfgfile_parser
    if config_parser.has_option('MASTER', 'load-plugins'):
        plugins = splitstrip(config_parser.get('MASTER', 'load-plugins'))
        linter.load_plugin_modules(plugins)
    # now we can load file config and command line, plugins (which can
    # provide options) have been registered
    linter.load_config_file()

    args = linter.load_command_line_configuration(pylint_args)

    if not args:
        print linter.help()
        sys.exit(2)

    # disable the warnings about disabling warnings...
    linter.disable('I0011')
    linter.disable('I0012')
    linter.disable('I0020')
    linter.disable('I0021')

    # insert current working directory to the python path to have a correct behaviour
    linter.prepare_import_path(args)

    # note: Pylint will exit with a status code indicating the health of the
    # code it was checking. Prospector will not mimic this behaviour, as it
    # interferes with scripts which depend on and expect the exit code of the
    # code checker to match whether the check itself was successful
    # TODO: add a command line argument to re-enable the exit code behaviour of pylint
    linter.check(args)
    sys.exit(0)


if __name__ == '__main__':
    run()
