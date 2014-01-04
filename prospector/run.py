import sys
import argparse
import os
import re
from datetime import datetime
from prospector.adaptor import LIBRARY_ADAPTORS
from prospector.adaptor.common import CommonAdaptor
from prospector.adaptor.profile import ProfileAdaptor
from prospector.autodetect import autodetect_libraries
from prospector.formatters import FORMATTERS
from prospector import tools, blender
from prospector import __pkginfo__
from prospector.message import Location, Message


def make_arg_parser():
    version = __pkginfo__.get_version()
    parser = argparse.ArgumentParser(
        description="Version %s. Performs analysis of Python code" % version
    )

    parser.add_argument(
        '-A', '--no-autodetect', action='store_true', default=False,
        help='Turn off auto-detection of frameworks and libraries used. By'
        ' default, autodetection will be used. To specify manually, see'
        ' the --uses option.',
    )

    parser.add_argument(
        '-B', '--no-blending', action='store_true', default=False,
        help="Turn off blending of messages. Prospector will merge together"
        " messages from different tools if they represent the same error."
        " Use this option to see all unmerged messages."
    )

    parser.add_argument(
        '-D', '--doc-warnings', action='store_true', default=False,
        help="Include warnings about documentation.",
    )

    parser.add_argument(
        '-M', '--messages-only', default=False, action='store_true',
        help="Only output message information (don't output summary"
        " information about the checks)",
    )

    output_help = "The output format. Valid values are %s" % (
        ', '.join(sorted(FORMATTERS.keys())),
    )
    parser.add_argument(
        '-o', '--output-format', default='text', help=output_help
    )

    parser.add_argument(
        '-p', '--path',
        help="The path to the python project to inspect (defaults to PWD)",
    )

    profiles_help = "The list of profiles to load. A profile is a certain" \
        " 'type' of behaviour for prospector, and is represented by a YAML" \
        " configuration file. A full path to the YAML file describing the" \
        " profile must be provided. (see --strictness)"
    parser.add_argument(
        '-P', '--profiles', default=[], nargs='+', help=profiles_help,
    )

    strictness_help = 'How strict the checker should be. This affects how' \
        ' harshly the checker will enforce coding guidelines. The default' \
        ' value is "medium", possible values are "veryhigh", "high",' \
        ' "medium", "low" and "verylow".'
    parser.add_argument(
        '-s', '--strictness', help=strictness_help, default='medium',
    )

    parser.add_argument(
        '-S', '--summary-only', default=False, action='store_true',
        help="Only output summary information about the checks (don't output"
        " message information)",
    )

    parser.add_argument(
        '-8', '--no-style-warnings', default=False, action='store_true',
        help="Don't create any warnings about style. This disables the PEP8 tool and"
        " similar checks for formatting."
    )

    tools_help = 'A list of tools to run. Possible values are: %s. By' \
        ' default, the following tools will be run: %s' % (
            ', '.join(sorted(tools.TOOLS.keys())),
            ', '.join(sorted(tools.DEFAULT_TOOLS))
        )
    parser.add_argument(
        '-t', '--tools', default=None, nargs='+', help=tools_help,
    )

    parser.add_argument(
        '-T', '--test-warnings', default=False, action='store_true',
        help="Also check test modules and packages",
    )

    uses_help = 'A list of one or more libraries or frameworks that the' \
        ' project users. Possible values are django, celery. This will be' \
        ' autodetected by default, but if autotectection doesn\'t work,' \
        ' manually specify them using this flag.'
    parser.add_argument(
        '-u', '--uses', help=uses_help, default=[], nargs='+',
    )

    parser.add_argument(
        '-v', '--version', action='store_true',
        help="Print version information and exit",
    )

    parser.add_argument(
        '--absolute-paths', action='store_true', default=False,
        help='Whether to output absolute paths when referencing files in'
        ' messages. By default, paths will be relative to the --path value',
    )

    parser.add_argument(
        '--die-on-tool-error', action='store_true', default=False,
        help='If a tool fails to run, prospector will try to carry on. Use '
        ' this flag to cause prospector to die and raise the exception the '
        ' tool generated. Mostly useful for development on prospector.'
    )

    parser.add_argument(
        '--no-common-plugin', action='store_true', default=False,
    )

    return parser


def _die(message):
    sys.stderr.write('%s\n' % message)
    sys.exit(1)


def run():
    parser = make_arg_parser()
    args = parser.parse_args()

    if args.version:
        sys.stdout.write("Prospector version %s\n" % __pkginfo__.get_version())
        sys.exit(0)

    summary = {
        'started': datetime.now()
    }

    path = args.path or os.path.abspath(os.getcwd())

    try:
        formatter = FORMATTERS[args.output_format]
        summary['formatter'] = args.output_format
    except KeyError:
        _die("Formatter %s is not valid - possible values are %s" % (
            args.output_format,
            ', '.join(FORMATTERS.keys()),
        ))

    libraries_used = []
    profiles = []
    adaptors = []

    if not args.no_common_plugin:
        adaptors.append(CommonAdaptor())
    if not args.no_autodetect:
        for libname, adaptor in autodetect_libraries(path):
            libraries_used.append(libname)
            adaptors.append(adaptor)

    strictness = args.strictness
    strictness_options = ('veryhigh', 'high', 'medium', 'low', 'verylow')
    if strictness not in strictness_options:
        possible = ', '.join(strictness_options)
        _die(
            "%s is not a valid value for strictness - possible values are %s" %
            (strictness, possible)
        )
    else:
        profiles.append('strictness_%s' % strictness)
        summary['strictness'] = strictness

    for library in args.uses:
        if library not in LIBRARY_ADAPTORS:
            possible = ', '.join(LIBRARY_ADAPTORS.keys())
            _die(
                "Library/framework %s is not valid - possible values are %s" %
                (library, possible)
            )
        libraries_used.append(library)
        adaptors.append(LIBRARY_ADAPTORS[library]())

    summary['libraries'] = ', '.join(libraries_used)

    if not args.doc_warnings:
        profiles.append('no_doc_warnings')

    if not args.test_warnings:
        profiles.append('no_test_warnings')

    if args.no_style_warnings:
        profiles.append('no_pep8')

    profiles += args.profiles

    profile_adaptor = ProfileAdaptor(profiles)
    adaptors.append(profile_adaptor)

    summary['adaptors'] = []
    for adaptor in adaptors:
        summary['adaptors'].append(adaptor.name)
    summary['adaptors'] = ', '.join(summary['adaptors'])

    tool_runners = []
    tool_names = args.tools or tools.DEFAULT_TOOLS
    for tool in tool_names:
        if not tool in tools.TOOLS:
            _die("Tool %s is not valid - possible values are %s" % (
                tool,
                ', '.join(tools.TOOLS.keys())
            ))
        if not profile_adaptor.is_tool_enabled(tool):
            continue
        tool_runners.append(tools.TOOLS[tool]())

    summary['tools'] = ', '.join(tool_names)

    ignore = [re.compile(ignore) for ignore in profile_adaptor.profile.ignore]

    for tool in tool_runners:
        tool.prepare(path, ignore, args, adaptors)

    messages = []
    for tool in tool_runners:
        try:
            messages += tool.run()
        except Exception:
            if args.die_on_tool_error:
                raise
            loc = Location(path, None, None, None, None)
            message = "Tool %s failed to run (exception was raised)" % tool.__class__.__name__
            msg = Message(tool.__class__.__name__, 'failure', loc, message=message)
            messages.append(msg)

    for message in messages:
        if args.absolute_paths:
            message.to_absolute_path(path)
        else:
            message.to_relative_path(path)

    if not args.no_blending:
        messages = blender.blend(messages)

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
