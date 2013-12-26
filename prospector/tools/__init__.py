from prospector.tools.dodgy import DodgyTool
from prospector.tools.pylint import PylintTool

TOOLS = {
    'pylint': PylintTool,
    'dodgy': DodgyTool,
}

DEFAULT_TOOLS = (
    'pylint',
    'dodgy',
)
