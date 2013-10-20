import sys
import argparse
import os
from datetime import datetime
from prospector.adaptor import CommonAdaptor, NoDocWarningsAdaptor, LIBRARY_ADAPTORS, STRICTNESS_ADAPTORS
from prospector.formatters import FORMATTERS
from prospector import tools
from requirements_detector import find_requirements
from requirements_detector.detect import RequirementsNotFound


def make_arg_parser():
    parser = argparse.ArgumentParser(description="Performs analysis of Python code")

    parser.add_argument('-A', '--no-autodetect', action='store_true', default=False,
                        help='Turn off auto-detection of frameworks and libraries used. By default, autodetection'
                             ' will be used. To specify manually, see the --uses option.')

    parser.add_argument('-D', '--no-doc-warnings', action='store_true', default=False,
                        help="Don't include any documentation warnings.")

    parser.add_argument('-M', '--messages-only', default=False, action='store_true',
                        help="Only output message information (don't output summary information about the checks)")

    output_help = "The output format. Valid values are %s" % ', '.join(FORMATTERS.keys())
    parser.add_argument('-o', '--output-format', default='text', help=output_help)

    parser.add_argument('-p', '--path', help="The path to the python project to inspect (defaults to PWD)")

    strictness_help = 'How strict the checker should be. This affects how harshly the checker will enforce' \
                      ' coding guidelines. The default value is "medium", possible values are "veryhigh", "high",' \
                      ' "medium", "low" and "verylow".'
    parser.add_argument('-s', '--strictness', help=strictness_help, default='medium')

    parser.add_argument('-S', '--summary-only', default=False, action='store_true',
                        help="Only output summary information about the checks (don't output message information)")

    tools_help = 'A list of tools to run. Possible values are: %s. By default, the following tools will be ' \
                 'run: %s' % (', '.join(tools.TOOLS.keys()), ', '.join(tools.DEFAULT_TOOLS))
    parser.add_argument('-t', '--tools', default=None, nargs='+', help=tools_help)

    uses_help = 'A list of one or more libraries or frameworks that the project users. Possible' \
                ' values are django, celery. This will be autodetected by default, but if autotectection' \
                ' doesn\'t work, manually specify them using this flag.'
    parser.add_argument('-u', '--uses', help=uses_help, default=[], nargs='+')

    parser.add_argument('--no-common-plugin', action='store_true', default=False)

    return parser


def _die(message):
    sys.stderr.write('%s\n' % message)
    sys.exit(1)


def autodetect_libraries(path):
    try:
        reqs = find_requirements(path)
    except RequirementsNotFound:
        return

    for requirement in reqs:
        if requirement.name is not None and requirement.name.lower() in LIBRARY_ADAPTORS:
            yield LIBRARY_ADAPTORS[requirement.name.lower()]()


def run():
    parser = make_arg_parser()
    args = parser.parse_args()

    summary = {
        'started': datetime.now()
    }

    path = args.path or os.getcwd()

    try:
        formatter = FORMATTERS[args.output_format]
        summary['formatter'] = args.output_format
    except KeyError:
        _die("Formatter %s is not valid - possible values are %s" % (args.output_format, ', '.join(FORMATTERS.keys())))

    adaptors = []
    if not args.no_common_plugin:
        adaptors.append(CommonAdaptor())
    if args.no_doc_warnings:
        adaptors.append(NoDocWarningsAdaptor())
    if not args.no_autodetect:
        adaptors += autodetect_libraries(path)

    strictness = args.strictness
    if strictness not in STRICTNESS_ADAPTORS:
        possible = ', '.join(STRICTNESS_ADAPTORS.keys())
        _die("%s is not a valid value for strictness - possible values are %s" % (strictness, possible))
    else:
        adaptors.append(STRICTNESS_ADAPTORS[strictness]())
        summary['strictness'] = strictness

    for library in args.uses:
        if library not in LIBRARY_ADAPTORS:
            possible = ', '.join(LIBRARY_ADAPTORS.keys())
            _die("Library/framework %s is not valid - possible values are %s" % (library, possible))
        adaptors.append(LIBRARY_ADAPTORS[library]())

    summary['adaptors'] = []
    for adaptor in adaptors:
        summary['adaptors'].append(adaptor.name)
    summary['adaptors'] = ', '.join(summary['adaptors'])

    tool_runners = []
    tool_names = args.tools or tools.DEFAULT_TOOLS
    for tool in tool_names:
        if not tool in tools.TOOLS:
            _die("Tool %s is not valid - possible values are %s" % (tool, ', '.join(tools.TOOLS.keys())))
        tool_runners.append(tools.TOOLS[tool]())

    summary['tools'] = ', '.join(tool_names)

    for tool in tool_runners:
        tool.prepare(path, args, adaptors)

    messages = []
    for tool in tool_runners:
        messages += tool.run()

    summary['message_count'] = len(messages)
    summary['completed'] = datetime.now()
    delta = (summary['completed'] - summary['started'])
    summary['time_taken'] = '%0.2f' % delta.total_seconds()

    summary['started'] = str(summary['started'])
    summary['completed'] = str(summary['completed'])

    if args.messages_only:
        summary = None
    if args.summary_only:
        messages = None

    formatter(summary, messages)

    sys.exit(0)


if __name__ == '__main__':
    run()
