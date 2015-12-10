# -*- coding: utf-8 -*-
from __future__ import absolute_import

from pyflakes.api import checkPath
from pyflakes.reporter import Reporter

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'PyFlakesTool',
)


# Prospector uses the same pyflakes codes as flake8 defines,
# see http://flake8.readthedocs.org/en/latest/warnings.html
# and https://bitbucket.org/tarek/flake8/src/a209fb69350c572c9b2d7b4b09c7657be153be5e/flake8/_pyflakes.py
_MESSAGE_CODES = {
    'UnusedImport': 'F401',
    'ImportShadowedByLoopVar': 'F402',
    'ImportStarUsed': 'F403',
    'LateFutureImport': 'F404',
    'Redefined': 'F810',
    'RedefinedWhileUnused': 'F811',
    'RedefinedInListComp': 'F812',
    'UndefinedName': 'F821',
    'UndefinedExport': 'F822',
    'UndefinedLocal': 'F823',
    'DuplicateArgument': 'F831',
    'UnusedVariable': 'F841',
}

# The old prospector codes were deprecated in favour of using the codes
# defined by flake8. This maps the old codes to the new codes.
LEGACY_CODE_MAP = {
    'FL0001': 'F401',
    'FL0002': 'F811',
    'FL0003': 'F812',
    'FL0004': 'F402',
    'FL0005': 'F403',
    'FL0006': 'F821',
    'FL0008': 'F822',
    'FL0009': 'F823',
    'FL0010': 'F831',
    'FL0011': 'F810',
    'FL0012': 'F404',
    'FL0013': 'F841',
}


class ProspectorReporter(Reporter):
    def __init__(self, ignore=None):
        super(ProspectorReporter, self).__init__(None, None)
        self._messages = []
        self.ignore = ignore or ()

    # pylint: disable=too-many-arguments
    def record_message(
            self,
            filename=None,
            line=None,
            character=None,
            code=None,
            message=None):

        code = code or 'F999'
        if code in self.ignore:
            return

        location = Location(
            path=filename,
            module=None,
            function=None,
            line=line,
            character=character,
        )
        message = Message(
            source='pyflakes',
            code=code,
            location=location,
            message=message,
        )
        self._messages.append(message)

    def unexpectedError(self, filename, msg):  # noqa
        self.record_message(
            filename=filename,
            code='F999',
            message=msg,
        )

    # pylint: disable=too-many-arguments
    def syntaxError(self, filename, msg, lineno, offset, text):  # noqa
        self.record_message(
            filename=filename,
            line=lineno,
            character=offset,
            code='F999',
            message=msg,
        )

    def flake(self, message):
        code = _MESSAGE_CODES.get(message.__class__.__name__, 'F999')

        self.record_message(
            filename=message.filename,
            line=message.lineno,
            character=(message.col + 1),
            code=code,
            message=message.message % message.message_args,
        )

    def get_messages(self):
        return self._messages


class PyFlakesTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(PyFlakesTool, self).__init__(*args, **kwargs)
        self.ignore_codes = ()

    def configure(self, prospector_config, _):
        ignores = prospector_config.get_disabled_messages('pyflakes')
        # convert old style to new
        self.ignore_codes = [LEGACY_CODE_MAP.get(code, code) for code in ignores]

    def run(self, found_files):
        reporter = ProspectorReporter(ignore=self.ignore_codes)
        for filepath in found_files.iter_module_paths():
            checkPath(filepath, reporter)

        return reporter.get_messages()
