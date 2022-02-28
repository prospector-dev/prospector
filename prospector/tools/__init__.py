from prospector.exceptions import FatalProspectorException
from prospector.tools.base import ToolBase
from prospector.tools.dodgy import DodgyTool
from prospector.tools.mccabe import McCabeTool
from prospector.tools.profile_validator import ProfileValidationTool
from prospector.tools.pycodestyle import PycodestyleTool
from prospector.tools.pydocstyle import PydocstyleTool
from prospector.tools.pyflakes import PyFlakesTool
from prospector.tools.pylint import PylintTool


def _tool_not_available(name, install_option_name):
    class NotAvailableTool(ToolBase):
        def configure(self, prospector_config, found_files):
            pass

        def run(self, _):
            raise FatalProspectorException(
                "\nCannot run tool %s as support was not installed.\n"
                "Please install by running 'pip install prospector[%s]'\n\n" % (name, install_option_name)
            )

    return NotAvailableTool


def _optional_tool(name, package_name=None, tool_class_name=None, install_option_name=None):
    package_name = "prospector.tools.%s" % (package_name or name)
    tool_class_name = tool_class_name or "%sTool" % name.title()
    install_option_name = install_option_name or ("with_%s" % name)

    try:
        tool_package = __import__(package_name, fromlist=[tool_class_name])
    except ImportError:
        tool_class = _tool_not_available(name, install_option_name)
    else:
        tool_class = getattr(tool_package, tool_class_name)

    return tool_class


TOOLS = {
    "dodgy": DodgyTool,
    "mccabe": McCabeTool,
    "pyflakes": PyFlakesTool,
    "pycodestyle": PycodestyleTool,
    "pylint": PylintTool,
    "pydocstyle": PydocstyleTool,
    "profile-validator": ProfileValidationTool,
    "frosted": _optional_tool("frosted"),
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
