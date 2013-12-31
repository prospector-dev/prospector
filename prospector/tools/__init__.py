from prospector.tools.pep8 import Pep8Tool
from prospector.tools.pylint import PylintTool

TOOLS = {
    'pep8': Pep8Tool,
    'pylint': PylintTool,
}

DEFAULT_TOOLS = (
    'pep8',
    'pylint',
)
