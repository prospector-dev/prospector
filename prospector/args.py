
from prospector import __pkginfo__
from prospector import tools
import argparse
from prospector.formatters import FORMATTERS


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
        '-e', '--external-config', default='only', choices=('none', 'merge', 'only'),
        help='Determines how prospector should behave when configuration already'
             ' exists for a tool. By default, prospector will use existing'
             ' configuration. A value of "merge" will cause prospector to '
             ' merge existing config and its own config, and "none" means'
             ' that prospector will use only its own config.'
    )

    parser.add_argument(
        '-I', '--ignore-patterns', nargs='+',
        help='A list of paths to ignore, as a list of regular expressions.'
             ' Files and folders will be ignored if their full path contains'
             ' any of these patterns.'
    )

    parser.add_argument(
        '-i', '--ignore-paths', nargs='+',
        help='A list of file or directory names to ignore. If the complete'
             ' name matches any of the items in this list, the file or '
             ' directory (and all subdirectories) will be ignored.'
    )

    parser.add_argument(
        '-M', '--messages-only', default=False, action='store_true',
        help="Only output message information (don't output summary"
             " information about the checks)",
        )

    parser.add_argument(
        '-o', '--output-format', default='text', help="The output format.",
        choices=sorted(FORMATTERS.keys())
    )

    parser.add_argument(
        '-p', '--path',
        help="The path to the python project to inspect (defaults to PWD)",
        )

    parser.add_argument(
        'checkpath', nargs='?', default=None,
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
                      ' value is "medium".'
    parser.add_argument(
        '-s', '--strictness', help=strictness_help, default='medium',
        choices=("veryhigh", "high", "medium", "low", "verylow")
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

    parser.add_argument(
        '-F', '--full-pep8', default=False, action='store_true',
        help="Enables every PEP8 warning, so that all PEP8 style violations will be"
             " reported."
    )

    tools_help = 'A list of tools to run. Possible values are: %s. By' \
                 ' default, the following tools will be run: %s' % (
                     ', '.join(sorted(tools.TOOLS.keys())),
                     ', '.join(sorted(tools.DEFAULT_TOOLS))
                 )
    parser.add_argument(
        '-t', '--tools', default=None, nargs='+', help=tools_help,
        choices=sorted(tools.TOOLS.keys())
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