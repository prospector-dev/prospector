from prospector.tools.dodgy import DodgyTool
from prospector.tools.frosted import FrostedTool
from prospector.tools.pep8 import Pep8Tool
from prospector.tools.pyflakes import PyFlakesTool
from prospector.tools.pylint import PylintTool
from prospector.tools.mccabe import McCabeTool


TOOLS = {
    'dodgy': DodgyTool,
    'frosted': FrostedTool,
    'mccabe': McCabeTool,
    'pyflakes': PyFlakesTool,
    'pep8': Pep8Tool,
    'pylint': PylintTool,
}


DEFAULT_TOOLS = (
    'dodgy',
    'frosted',
    'mccabe',
    'pyflakes',
    'pep8',
    'pylint',
)
