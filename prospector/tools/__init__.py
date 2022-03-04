import importlib

from prospector.exceptions import FatalProspectorException
from prospector.tools.base import ToolBase
from prospector.tools.dodgy import DodgyTool
from prospector.tools.mccabe import McCabeTool
from prospector.tools.pycodestyle import PycodestyleTool
from prospector.tools.pydocstyle import PydocstyleTool
from prospector.tools.pyflakes import PyFlakesTool
from prospector.tools.pylint import PylintTool


def _tool_not_available(name, install_option_name):
    class NotAvailableTool(ToolBase):
        """
        Dummy tool class to return when a particular dependency is not found (such as mypy, or bandit)
        for an optional tool. This does not error immediately since the tool is optional, but rather
        if the user tries to run prospector and specifies using the tool at which point an error is raised.
        """

        def configure(self, prospector_config, found_files):
            pass

        def run(self, _):
            raise FatalProspectorException(
                f"\nCannot run tool {name} as support was not installed.\n"
                f"Please install by running 'pip install prospector[{install_option_name}]'\n\n"
            )

    return NotAvailableTool


def _optional_tool(name, package_name=None, tool_class_name=None, install_option_name=None):
    package_name = "prospector.tools.%s" % (package_name or name)
    tool_class_name = tool_class_name or f"{name.title()}Tool"
    install_option_name = install_option_name or f"with_{name}"

    try:
        tool_package = __import__(package_name, fromlist=[tool_class_name])
    except ImportError:
        tool_class = _tool_not_available(name, install_option_name)
    else:
        tool_class = getattr(tool_package, tool_class_name)

    return tool_class


def _profile_validator_tool(*args, **kwargs):
    # bit of a hack to avoid a cyclic import...
    mdl = importlib.import_module("prospector.tools.profile_validator")
    return mdl.ProfileValidationTool(*args, **kwargs)


TOOLS = {
    "dodgy": DodgyTool,
    "mccabe": McCabeTool,
    "pyflakes": PyFlakesTool,
    "pycodestyle": PycodestyleTool,
    "pylint": PylintTool,
    "pydocstyle": PydocstyleTool,
    "profile-validator": _profile_validator_tool,
    "vulture": _optional_tool("vulture"),
    "pyroma": _optional_tool("pyroma"),
    "mypy": _optional_tool("mypy"),
    "bandit": _optional_tool("bandit"),
}


DEFAULT_TOOLS = (
    "dodgy",
    "mccabe",
    "pyflakes",
    "pycodestyle",
    "pylint",
    "pydocstyle",
    "profile-validator",
)

DEPRECATED_TOOL_NAMES = {"pep8": "pycodestyle", "pep257": "pydocstyle"}
