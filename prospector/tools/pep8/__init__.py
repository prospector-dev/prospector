
from pep8 import StyleGuide, BaseReport, register_check
from pep8ext_naming import NamingChecker

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'Pep8Tool',
)


class ProspectorReport(BaseReport):
    def __init__(self, *args, **kwargs):
        super(ProspectorReport, self).__init__(*args, **kwargs)
        self._prospector_messages = []

    def error(self, line_number, offset, text, check):
        code = super(ProspectorReport, self).error(
            line_number,
            offset,
            text,
            check,
        )
        if code is None:
            # The error pep8 found is being ignored, let's move on.
            return
        else:
            # Get a clean copy of the message text without the code embedded.
            text = text[5:]

        # mixed indentation (E101) is a file global message
        if code == 'E101':
            line_number = None

        # Record the message using prospector's data structures.
        location = Location(
            path=self.filename,
            module=None,
            function=None,
            line=line_number,
            character=(offset + 1),
        )
        message = Message(
            source='pep8',
            code=code,
            location=location,
            message=text,
        )

        self._prospector_messages.append(message)

    def get_messages(self):
        return self._prospector_messages


class ProspectorStyleGuide(StyleGuide):
    def __init__(self, *args, **kwargs):
        # Remember the ignore patterns for later.
        self._ignore_patterns = kwargs.pop('ignore_patterns', [])

        # Override the default reporter with our custom one.
        kwargs['reporter'] = ProspectorReport

        super(ProspectorStyleGuide, self).__init__(*args, **kwargs)

    def excluded(self, filename, parent=None):
        if super(ProspectorStyleGuide, self).excluded(filename, parent):
            return True

        # If the file survived pep8's exclusion rules, check it against
        # prospector's patterns.
        if any([ip.search(filename) for ip in self._ignore_patterns]):
            return True

        return False


class Pep8Tool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(Pep8Tool, self).__init__(*args, **kwargs)
        self.checker = None

    def prepare(self, rootpath, ignore, args, adaptors):
        # Instantiate our custom pep8 checker.
        self.checker = ProspectorStyleGuide(
            paths=[rootpath],
            ignore_patterns=ignore,
        )

        # Make sure pep8's code ignores are fully reset to zero.
        # pylint: disable=W0201
        self.checker.select = ()
        self.checker.ignore = ()

        # Let the adaptors & profiles do their thing.
        for adaptor in adaptors:
            adaptor.adapt_pep8(self.checker)

    def run(self):
        report = self.checker.check_files()
        return report.get_messages()


# Load pep8ext_naming into pep8's configuration.
register_check(NamingChecker)
