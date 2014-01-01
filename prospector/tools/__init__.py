from prospector.tools.pyflakes import PyFlakesTool
from prospector.tools.pylint import PylintTool

TOOLS = {
    'pyflakes': PyFlakesTool,
    'pylint': PylintTool
}

DEFAULT_TOOLS = (
    'pyflakes',
    'pylint',
)
