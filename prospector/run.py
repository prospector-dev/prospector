import sys
import os
import re
from datetime import datetime
from prospector.adaptor import LIBRARY_ADAPTORS
from prospector.adaptor.common import CommonAdaptor
from prospector.adaptor.profile import ProfileAdaptor
from prospector.args import make_arg_parser
from prospector.autodetect import autodetect_libraries
from prospector.formatters import FORMATTERS
from prospector import tools, blender, __pkginfo__
from prospector.message import Location, Message


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

    path = args.path or args.checkpath or os.path.abspath(os.getcwd())

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

    if args.full_pep8:
        profiles.append('full_pep8')

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
    if args.ignore_patterns is not None:
        ignore += [re.compile(patt) for patt in args.ignore_patterns]
    if args.ignore_paths is not None:
        boundary = r"(^|/|\\)%s(/|\\|$)"
        ignore += [re.compile(boundary % re.escape(ignore_path)) for ignore_path in args.ignore_paths]

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
            for name, cls in tools.TOOLS.items():
                if cls == tool.__class__:
                    toolname = name
                    break
            else:
                toolname = 'Unknown'
            message = "Tool %s failed to run (exception was raised)" % toolname
            msg = Message(toolname, 'failure', loc, message=message)
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
