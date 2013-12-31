from prospector.tools.mccabe import McCabeTool
from prospector.tools.pylint import PylintTool

TOOLS = {
    'mccabe': McCabeTool,
    'pylint': PylintTool
}

DEFAULT_TOOLS = (
    'mccabe',
    'pylint',
)
