from __future__ import absolute_import

import os
import re
from pep8 import StyleGuide, BaseReport, register_check, DEFAULT_CONFIG, PROJECT_CONFIG
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
    def __init__(self, rootpath, *args, **kwargs):
        # Remember the ignore patterns for later.
        self._rootpath = rootpath
        self._ignore_patterns = kwargs.pop('ignore_patterns', [])

        # Override the default reporter with our custom one.
        kwargs['reporter'] = ProspectorReport

        super(ProspectorStyleGuide, self).__init__(*args, **kwargs)

    def excluded(self, filename, parent=None):
        if super(ProspectorStyleGuide, self).excluded(filename, parent):
            return True

        # If the file survived pep8's exclusion rules, check it against
        # prospector's patterns.
        fullpath = os.path.join(parent, filename) if parent else filename
        relpath = os.path.relpath(fullpath, self._rootpath)
        if any([ip.search(relpath) for ip in self._ignore_patterns]):
            return True

        return False


class Pep8Tool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(Pep8Tool, self).__init__(*args, **kwargs)
        self.checker = None

    def prepare(self, rootpath, ignore, args, adaptors):
        # figure out if we should use a pre-existing config file
        # such as setup.cfg or tox.ini
        external_config = None

        # 'none' means we ignore any external config, so just carry on
        if args.external_config != 'none':
            paths = [os.path.join(rootpath, name) for name in PROJECT_CONFIG]
            paths.append(DEFAULT_CONFIG)

            for conf_path in paths:
                if os.path.exists(conf_path) and os.path.isfile(conf_path):
                    # this file exists - but does it have pep8 config in it?
                    header = re.compile(r'\[pep8\]')
                    with open(conf_path) as f:
                        if any([header.search(line) for line in f.readlines()]):
                            external_config = conf_path
                            break

        if args.external_config == 'none':
            # if we should not use external config, we always want to
            # use prospector's config
            use_config = True

        elif args.external_config == 'merge':
            # if we should merge with any existing config, then we want
            # to merge prospector's config
            use_config = True

        elif args.external_config == 'only':
            # if we should only use external config, then we don't use
            # prospector's config *unless* there is no external config
            use_config = external_config is None

        # Instantiate our custom pep8 checker.
        self.checker = ProspectorStyleGuide(
            rootpath=rootpath,
            paths=[rootpath],
            ignore_patterns=ignore,
            config_file=external_config
        )

        if args.external_config == 'none' or external_config is None:
            # Make sure pep8's code ignores are fully reset to zero.
            # pylint: disable=W0201
            self.checker.select = ()
            self.checker.ignore = ()

        # Let the adaptors & profiles do their thing.
        for adaptor in adaptors:
            adaptor.adapt_pep8(self.checker, use_config=use_config)

        # if we have a command line --max-line-length argument, that
        # overrules everything
        if args.max_line_length is not None:
            self.checker.options.max_line_length = args.max_line_length

    def run(self):
        report = self.checker.check_files()
        return report.get_messages()


# Load pep8ext_naming into pep8's configuration.
register_check(NamingChecker)
