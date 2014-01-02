from prospector.tools.dodgy import DodgyTool
from prospector.tools.pylint import PylintTool
from prospector.tools.mccabe import McCabeTool
from prospector.tools.pylint import PylintTool

TOOLS = {
    'pylint': PylintTool,
    'dodgy': DodgyTool,
    'mccabe': McCabeTool,
}

DEFAULT_TOOLS = (
    'mccabe',
    'pylint',
    'dodgy',
)
