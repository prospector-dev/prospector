# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import re
from pycodestyle import StyleGuide, BaseReport, register_check, PROJECT_CONFIG
from pep8ext_naming import NamingChecker

try:
    # for pep8 <= 1.5.7
    from pycodestyle import DEFAULT_CONFIG as USER_CONFIG
except ImportError:
    # for pep8 >= 1.6.0
    from pycodestyle import USER_CONFIG

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
    def __init__(self, found_files, *args, **kwargs):
        self._files = found_files
        self._module_paths = set(self._files.iter_module_paths())

        # Override the default reporter with our custom one.
        kwargs['reporter'] = ProspectorReport

        super(ProspectorStyleGuide, self).__init__(*args, **kwargs)

    def excluded(self, filename, parent=None):
        if super(ProspectorStyleGuide, self).excluded(filename, parent):
            return True

        # If the file survived pep8's exclusion rules, check it against
        # prospector's patterns.
        if os.path.isdir(os.path.join(self._files.rootpath, filename)):
            return False

        fullpath = os.path.join(self._files.rootpath, parent, filename) if parent else filename
        return fullpath not in self._module_paths


class Pep8Tool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(Pep8Tool, self).__init__(*args, **kwargs)
        self.checker = None

    def configure(self, prospector_config, found_files):
        # figure out if we should use a pre-existing config file
        # such as setup.cfg or tox.ini
        external_config = None

        # 'none' means we ignore any external config, so just carry on
        use_config = False

        if prospector_config.use_external_config('pep8'):
            use_config = True

            paths = [os.path.join(found_files.rootpath, name) for name in PROJECT_CONFIG]
            paths.append(USER_CONFIG)
            ext_loc = prospector_config.external_config_location('pep8')
            if ext_loc is not None:
                paths = [ext_loc] + paths

            for conf_path in paths:
                if os.path.exists(conf_path) and os.path.isfile(conf_path):
                    # this file exists - but does it have pep8 config in it?
                    header = re.compile(r'\[pep8\]')
                    with open(conf_path) as conf_file:
                        if any([header.search(line) for line in conf_file.readlines()]):
                            external_config = conf_path
                            break

        # Instantiate our custom pep8 checker.
        self.checker = ProspectorStyleGuide(
            paths=list(found_files.iter_package_paths()),
            found_files=found_files,
            config_file=external_config
        )

        if not use_config or external_config is None:
            configured_by = None
            # This means that we don't have existing config to use.
            # Make sure pep8's code ignores are fully reset to zero before
            # adding prospector-flavoured configuration.
            # pylint: disable=attribute-defined-outside-init
            self.checker.options.select = ()
            self.checker.options.ignore = tuple(prospector_config.get_disabled_messages('pep8'))

            if 'max-line-length' in prospector_config.tool_options('pep8'):
                self.checker.options.max_line_length = \
                    prospector_config.tool_options('pep8')['max-line-length']
        else:
            configured_by = "Configuration found at %s" % external_config

        # if we have a command line --max-line-length argument, that
        # overrules everything
        max_line_length = prospector_config.max_line_length
        if max_line_length is not None:
            self.checker.options.max_line_length = max_line_length

        return configured_by, []

    def run(self, _):
        report = self.checker.check_files()
        return report.get_messages()


# Load pep8ext_naming into pep8's configuration.
register_check(NamingChecker)
