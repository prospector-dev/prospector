import sys
from prospector.tools.base import ToolBase
from prospector.tools.dodgy import DodgyTool
from prospector.tools.frosted import FrostedTool
from prospector.tools.pep8 import Pep8Tool
from prospector.tools.pyflakes import PyFlakesTool
from prospector.tools.pylint import PylintTool
from prospector.tools.mccabe import McCabeTool


def _tool_not_available(name, install_option_name):
    class NotAvailableTool(ToolBase):
        def run(self):
            sys.stderr.write("Cannot run tool %s as support was not installed.\n"
                             "Please install by running 'pip install prospector[%s]\n'" % (name, install_option_name))
            sys.exit(1)

    return NotAvailableTool


def _optional_tool(name, package_name=None, tool_class_name=None, install_option_name=None):
    package_name = 'prospector.tools.%s' % (package_name or name)
    tool_class_name = tool_class_name or '%sTool' % name.title()
    install_option_name = install_option_name or ('with_%s' % name)

    try:
        tool_package = __import__(package_name, fromlist=[tool_class_name])
    except ImportError:
        tool_class = _tool_not_available(name, install_option_name)
    else:
        tool_class = getattr(tool_package, tool_class_name)

    return tool_class


TOOLS = {
    'dodgy': DodgyTool,
    'frosted': FrostedTool,
    'mccabe': McCabeTool,
    'pyflakes': PyFlakesTool,
    'pep8': Pep8Tool,
    'pylint': PylintTool,
    'vulture': _optional_tool('vulture'),
    'pyroma': _optional_tool('pyroma'),
    'pep257': _optional_tool('pep257'),
}


DEFAULT_TOOLS = (
    'dodgy',
    'frosted',
    'mccabe',
    'pyflakes',
    'pep8',
    'pylint'
)
