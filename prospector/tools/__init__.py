from prospector.tools.dodgy import DodgyTool
from prospector.tools.pyflakes import PyFlakesTool
from prospector.tools.pylint import PylintTool
from prospector.tools.mccabe import McCabeTool
from prospector.tools.pylint import PylintTool

TOOLS = {
    'pylint': PylintTool,
}

TOOLS = {
    'dodgy': DodgyTool,
    'mccabe': McCabeTool,
    'pyflakes': PyFlakesTool,
    'pylint': PylintTool,
}

DEFAULT_TOOLS = (
    'dodgy',
    'mccabe',
    'pyflakes',
    'pylint',
)
