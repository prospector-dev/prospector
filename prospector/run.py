import sys
import argparse
import os
from prospector.formatters import FORMATTERS
from prospector.profiles import PROFILES
from prospector import tools
from requirements_detector import find_requirements
from requirements_detector.detect import RequirementsNotFound


def make_arg_parser():
    parser = argparse.ArgumentParser(description="Performs analysis of Python code")

    profile_help = 'A list of one or more profiles to use.'
    parser.add_argument('-P', '--profiles', help=profile_help, default=[], nargs='+')

    output_help = "The output format. Valid values are 'json' and 'text'"
    parser.add_argument('-o', '--output-format', default='text', help=output_help)

    parser.add_argument('-A', '--no-autodetect', action='store_true', default=False,
                        help='Turn off auto-detection of frameworks and libraries used. By default, autodetection'
                             ' will be used.')

    parser.add_argument('--no-common-profile', action='store_true', default=False)

    tools_help = 'A list of tools to run. Possible values are: %s. By default, the following tools will be ' \
                 'run: %s' % (', '.join(tools.TOOLS.keys()), ', '.join(tools.DEFAULT_TOOLS))
    parser.add_argument('-t', '--tools', default=None, nargs='+', help=tools_help)

    parser.add_argument('path', nargs='?', help="The path to the python project to inspect (defaults to PWD)")
    parser.add_argument('-p', '--path', help="The path to the python project to inspect (defaults to PWD)")

    return parser


def _die(message):
    sys.stderr.write('%s\n' % message)
    sys.exit(1)


def autodetect_profiles(path):
    try:
        reqs = find_requirements(path)
    except RequirementsNotFound:
        return

    for requirement in reqs:
        if requirement.name is not None and requirement.name.lower() in PROFILES:
            yield requirement.name.lower()


def run():
    parser = make_arg_parser()
    args = parser.parse_args()

    path = args.path or os.getcwd()

    try:
        formatter = FORMATTERS[args.output_format]()
    except KeyError:
        _die("Formatter %s is not valid - possible values are %s" % (args.output_format, ', '.join(FORMATTERS.keys())))

    profile_names = args.profiles
    if not args.no_common_profile:
        profile_names += ['common']
    if not args.no_autodetect:
        profile_names += autodetect_profiles(path)

    profiles = []
    for profile in profile_names:
        if profile not in PROFILES:
            _die("Profile %s is not valid - possible values are %s" % (profile, ', '.join(PROFILES.keys())))
        profiles.append(PROFILES[profile]())

    tool_runners = []
    tool_names = args.tools or tools.DEFAULT_TOOLS
    for tool in tool_names:
        if not tool in tools.TOOLS:
            _die("Tool %s is not valid - possible values are %s" % (tool, ', '.join(tools.TOOLS.keys())))
        tool_runners.append(tools.TOOLS[tool]())

    for tool in tool_runners:
        tool.prepare(path, args, profiles)

    messages = []
    for tool in tool_runners:
        messages += tool.run()

    formatter.format_messages(messages)

    sys.exit(0)


if __name__ == '__main__':
    run()
