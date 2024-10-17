import argparse
import configparser
import os
import sys
from enum import Enum
from typing import Any, List, Optional, Union, get_args, get_origin

import toml  # type: ignore[import-untyped]
import yaml
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from prospector.config.datatype import parse_output_format
from prospector.formatters import FORMATTERS
from prospector.tools import DEFAULT_TOOLS, TOOLS


class Strictness(Enum):
    veryhigh = "veryhigh"
    high = "high"
    medium = "medium"
    low = "low"
    verylow = "verylow"
    none = "none"
    from_profile = "from profile"


class ProspectorConfiguration(BaseModel):
    """
    The configuration for Prospector.
    """

    zero_exit: bool = False
    autodetect: bool = True
    uses: list[str] = []
    blending: bool = True
    doc_warnings: Optional[bool] = None
    test_warnings: Optional[bool] = None
    no_style_warnings: Optional[bool] = None
    member_warnings: Optional[bool] = None
    full_pep8: Optional[bool] = None
    max_line_length: Optional[int] = None
    messages_only: bool = False
    summary_only: bool = False
    quiet: bool = False
    output_format: Optional[list[tuple[str, list[str]]]] = None
    absolute_paths: bool = False
    tools: Optional[list[str]] = None
    with_tools: list[str] = []
    without_tools: list[str] = []
    profiles: list[str] = []
    profile_path: list[str] = []
    strictness: Optional[Strictness] = None
    show_profile: bool = False
    no_external_config: bool = False
    legacy_tool_names: bool = False
    pylint_config_file: Optional[str] = None
    path: Optional[str] = None
    ignore_patterns: list[str] = []
    ignore_paths: list[str] = []
    die_on_tool_error: bool = False
    include_tool_stdout: bool = False
    direct_tool_stdout: bool = False


def _parse_value(
    name: str, value_str: str, conf: FieldInfo
) -> Optional[Union[bool, int, float, str, list[bool], list[int], list[float], list[str]]]:
    value: Any = None

    type_ = conf.annotation
    origin = get_origin(type_)
    if origin is Union:
        args = get_args(type_)
        if args[1] is type(None):
            type_ = args[0]
            origin = get_origin(type_)

    if origin is None:
        if type_ is bool:
            value = value_str.lower() in ("1", "true", "yes")
        elif type_ is int:
            value = int(value_str)
        elif type_ is float:
            value = float(value_str)
        elif type_ is str:
            value = value_str
        else:
            # Enum
            value = type_(value_str)
    else:
        if origin == list:
            sub_type = get_args(type_)[0]
            if sub_type is str:
                value = value_str.split(",")
            elif sub_type is bool:
                value = [x.lower() in ("1", "true", "yes") for x in value_str.split(",")]
            elif sub_type is int:
                value = [int(x) for x in value_str.split(",")]
            elif sub_type is float:
                value = [float(x) for x in value_str.split(",")]
            else:
                # Enum
                value = [sub_type(x) for x in value_str.split(",")]

    if value is None:
        print(f"Could not parse {name}={value_str}")
    return value


def _get_prospector_rc_config(base_path: str) -> list[tuple[list[str], str]]:
    return [
        (["prospector"], base_path),
        (["prospector"], f"{base_path}.toml"),
        ([], f"{base_path}.yaml"),
        ([], f"{base_path}.yml"),
    ]


def get_config() -> ProspectorConfiguration:
    config = {}

    for keys, config_filename in (
        *_get_prospector_rc_config(os.path.expanduser(os.path.join("~", ".prospectorrc"))),
        *_get_prospector_rc_config(
            os.path.join(
                os.getenv("XDG_CONFIG_HOME") or os.path.expanduser(os.path.join("~", ".config")),
                ".prospectorrc",
            )
        ),
        *_get_prospector_rc_config(".prospectorrc"),
        (["prospector"], "setup.cfg"),
        (["prospector"], "tox.ini"),
        (["tool", "prospector"], "pyproject.toml"),
    ):
        if os.path.exists(config_filename):
            with open(config_filename) as f:
                if config_filename.endswith(".toml"):
                    new_config = toml.load(f)
                elif config_filename.endswith(".yaml") or config_filename.endswith(".yml"):
                    new_config = yaml.safe_load(f)
                else:
                    config_parser = configparser.ConfigParser()
                    config_parser.read_file(f)
                    new_config = {keys[0]: config_parser[keys[0]]} if keys[0] in config_parser else {}
            for key in keys:
                new_config = new_config.get(key, {})
            config.update(new_config)

    for name, conf in ProspectorConfiguration.model_fields.items():
        env_name = f"PROSPECTOR_{name.upper()}"
        if env_name in os.environ:
            value_str = os.environ[env_name]
            value = _parse_value(name, value_str, conf)
            if value is not None:
                config[name] = value

    args = build_command_line_parser().parse_args()
    for name, conf in ProspectorConfiguration.model_fields.items():
        if hasattr(args, name):
            value = getattr(args, name)
            if value is not None:
                config[name] = value

    try:
        if isinstance(config.get("output_format"), str):
            config["output_format"] = [parse_output_format(config["output_format"])]
        if isinstance(config.get("output_format"), list):
            for of, index in enumerate(config["output_format"]):
                if isinstance(index, str):
                    config["output_format"][of] = parse_output_format(index)
        ProspectorConfiguration.model_validate(config)
    except ValueError as e:
        print()
        print(e)
        sys.exit(1)
    return ProspectorConfiguration(**config)


# flake8: noqa
def build_command_line_parser(
    prog: str = "prospector", description: str = "Performs static analysis of Python code"
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog, description=description)

    parser.add_argument(
        "-0",
        "--zero-exit",
        action="store_true",
        help="Prospector will exit with a code of 1 (one) if any messages are found. This makes automation easier; if there are any problems at all, the exit code is non-zero. However this behavior is not always desirable, so if this flag is set, prospector will exit with a code of 0 if it ran successfully, and non-zero if it failed to run.",
    )
    parser.add_argument(
        "-A",
        "--no-autodetect",
        action="store_true",
        help="Turn off auto-detection of frameworks and libraries used. By default, autodetection will be used. To specify manually, see the --uses option.",
    )
    parser.add_argument(
        "-u",
        "--uses",
        action="append",
        help="A list of one or more libraries or frameworks that the project uses. Possible values are: django, celery, flask. This will be autodetected by default, but if autodetection doesn't work, manually specify them using this flag.",
    )
    parser.add_argument(
        "-B",
        "--no-blending",
        action="store_true",
        help="Turn off blending of messages. Prospector will merge together messages from different tools if they represent the same error. Use this option to see all unmerged messages.",
    )
    parser.add_argument("-D", "--doc-warnings", action="store_true", help="Include warnings about documentation.")
    parser.add_argument("-T", "--test-warnings", action="store_true", help="Also check test modules and packages.")
    parser.add_argument(
        "--legacy-tool-names",
        action="store_true",
        help="Output deprecated names for tools (pep8, pep257) instead of updated names (pycodestyle, pydocstyle)",
    )
    parser.add_argument(
        "-8",
        "--no-style-warnings",
        action="store_true",
        help="Don't create any warnings about style. This disables the PEP8 tool and similar checks for formatting.",
    )
    parser.add_argument(
        "-m",
        "--member-warnings",
        action="store_true",
        help="Attempt to warn when code tries to access an attribute of a class or member of a module which does not exist. This is disabled by default as it tends to be quite inaccurate.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Run but do not output anything to stdout. Useful to suppress output in scripts without sending to a file (via -o)",
    )
    parser.add_argument(
        "-F",
        "--full-pep8",
        action="store_true",
        help="Enables every PEP8 warning, so that all PEP8 style violation will be reported.",
    )
    parser.add_argument(
        "--max-line-length",
        type=int,
        help="The maximum line length allowed. This will be set by the strictness if no value is explicitly specified",
    )
    parser.add_argument(
        "-M",
        "--messages-only",
        action="store_true",
        help="Only output message information (don't output summary information about the checks)",
    )
    parser.add_argument(
        "-S",
        "--summary-only",
        action="store_true",
        help="Only output summary information about the checks (don't output message information)",
    )
    parser.add_argument(
        "-o",
        "--output-format",
        action="append",
        help="The output format. Valid values are: {}. This will output to stdout by default, however a target file can be used instead by adding :path-to-output-file, eg, -o json:output.json".format(
            ", ".join(sorted(FORMATTERS.keys()))
        ),
    )
    parser.add_argument(
        "--absolute-paths",
        action="store_true",
        help="Whether to output absolute paths when referencing files in messages. By default, paths will be relative to the project path",
    )
    parser.add_argument(
        "-t",
        "--tool",
        dest="tools",
        action="append",
        help="A list of tools to run. This lets you set exactly which tools to run. To add extra tools to the defaults, see --with-tool. Possible values are: {}. By default, the following tools will be run: {}".format(
            ", ".join(sorted(TOOLS.keys())), ", ".join(sorted(DEFAULT_TOOLS))
        ),
    )
    parser.add_argument(
        "-w",
        "--with-tool",
        dest="with_tools",
        action="append",
        help="A list of tools to run in addition to the default tools. To specify all tools explicitly, use the --tool argument. Possible values are {}.".format(
            ", ".join(sorted(TOOLS.keys()))
        ),
    )
    parser.add_argument(
        "-W",
        "--without-tool",
        dest="without_tools",
        action="append",
        help="A list of tools that should not be run. Useful to turn off only a single tool from the defaults. To specify all tools explicitly, use the --tool argument. Possible values are {}.".format(
            ", ".join(sorted(TOOLS.keys()))
        ),
    )
    parser.add_argument(
        "-P",
        "--profile",
        dest="profiles",
        action="append",
        help="The list of profiles to load. A profile is a certain 'type' of behavior for prospector, and is represented by a YAML configuration file. Either a full path to the YAML file describing the profile must be provided, or it must be on the profile path (see --profile-path)",
    )
    parser.add_argument(
        "--profile-path",
        action="append",
        help="Additional paths to search for profile files. By default this is the path that prospector will check, and a directory called '.prospector' in the path that prospector will check.",
    )
    parser.add_argument(
        "--show-profile",
        action="store_true",
        help="Include the computed profile in the summary. This will show what prospector has decided the overall profile is once all profiles have been combined and inherited from. This will produce a large output in most cases so is only useful when trying to debug why prospector is not behaving like you expect.",
    )
    parser.add_argument(
        "-s",
        "--strictness",
        help='How strict the checker should be. This affects how harshly the checker will enforce coding guidelines. The default value is "medium", possible values are "veryhigh", "high", "medium", "low" and "verylow".',
    )
    parser.add_argument(
        "-E",
        "--no-external-config",
        action="store_true",
        help="Determines how prospector should behave when configuration already exists for a tool. By default, prospector will use existing configuration. This flag will cause prospector to ignore existing configuration and use its own settings for every tool. Note that prospector will always use its own config for tools which do not have custom configuration.",
    )
    parser.add_argument(
        "--pylint-config-file",
        help="The path to a pylintrc file to use to configure pylint. Prospector will find .pylintrc files in the root of the project, but you can use this option to specify manually where it is.",
    )
    parser.add_argument(
        "-I",
        "--ignore-patterns",
        action="append",
        help="A list of paths to ignore, as a list of regular expressions. Files and folders will be ignored if their full path contains any of these patterns.",
    )
    parser.add_argument(
        "-i",
        "--ignore-paths",
        action="append",
        help="A list of file or directory names to ignore. If the complete name matches any of the items in this list, the file or directory (and all subdirectories) will be ignored.",
    )
    parser.add_argument(
        "-X",
        "--die-on-tool-error",
        action="store_true",
        help="If a tool fails to run, prospector will try to carry on. Use this flag to cause prospector to die and raise the exception the tool generated. Mostly useful for development on prospector.",
    )
    parser.add_argument(
        "--include-tool-stdout",
        action="store_true",
        help="There are various places where tools will output warnings to stdout/stderr, which breaks parsing of JSON output. Therefore while tols is running, this is suppressed. For developing, it is sometimes useful to see this. This flag will cause stdout/stderr from a tool to be shown as a normal message amongst other warnings. See also --direct-tool-stdout",
    )
    parser.add_argument(
        "--direct-tool-stdout",
        action="store_true",
        help="Same as --include-tool-stdout, except the output will be printed directly rather than shown as a message.",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="The path to a Python project to inspect. Defaults to PWD if not specified. Note: This command line argument is deprecated and will be removed in a future update. Please use the positional PATH argument instead.",
    )

    parser.add_argument(
        "path",
        help="The path to a Python project to inspect. Defaults to PWD if not specified. If multiple paths are specified, they must all be files (no directories).",
        metavar="PATH",
        nargs="?",
    )

    return parser
