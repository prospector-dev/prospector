from __future__ import absolute_import

import tokenize
from pylint.checkers import BaseTokenChecker
from pylint.interfaces import ITokenChecker


class IndentChecker(BaseTokenChecker):

    __implements__ = (ITokenChecker,)

    name = 'indentation'
    msgs = {
        'W0313': ('File contains mixed indentation - some lines use tabs, some lines use spaces',
                  'indentation-mixture',
                  'Used when there are some mixed tabs and spaces in a module.'),
        'W0314': ('Line uses %s for indentation, but %s required',
                  'incorrect-indentation',
                  'Used when the indentation of a line does not match the style required by configuration.')
    }
    options = (
        ('indent-strict-spaces',
         {'default': False, 'type': "yn", 'metavar': '<boolean>',
          'help': 'Enforce using only spaces for indentation'}),

        ('indent-strict-tabs',
         {'default': False, 'type': "yn", 'metavar': '<boolean>',
          'help': 'Enforce using only tabs for indentation'})
    )

    def process_tokens(self, tokens):
        tab_count = space_count = 0
        line_num = 0

        for token in tokens:
            if token[0] == tokenize.NEWLINE:
                line_num += 1
                line = token[4]
                if line.startswith('\t'):
                    if self.config.indent_strict_spaces:
                        # we have tabs but are configured to only allow spaces
                        self.add_message('incorrect-indentation', line=line_num, args=('tabs', 'spaces'))
                    tab_count += 1

                if line.startswith(' '):
                    if self.config.indent_strict_tabs:
                        # we have tabs but are configured to only allow spaces
                        self.add_message('incorrect-indentation', line=line_num, args=('spaces', 'tabs'))
                    space_count += 1

        if tab_count > 0 and space_count > 0:
            # this file has mixed indentation!
            self.add_message('indentation-mixture', line=-1)
