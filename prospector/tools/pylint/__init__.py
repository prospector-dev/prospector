from collections import defaultdict
import re
import sys
import os
from pylint.config import find_pylintrc
from pylint.utils import UnknownMessage
from prospector.message import Message
from prospector.tools.base import ToolBase
from prospector.tools.pylint.collector import Collector
from prospector.tools.pylint.indent_checker import IndentChecker
from prospector.tools.pylint.linter import ProspectorLinter


_UNUSED_WILDCARD_IMPORT_RE = re.compile(r'^Unused import (.*) from wildcard import$')


class DummyStream(object):
    def __init__(self):
        self.contents = ''

    def write(self, text):
        pass

    def close(self):
        pass

    def flush(self):
        pass


# The class name here is lowercase as it is a context manager, which
# typically tend to me lowercase.
class stdout_wrapper(object):  # noqa pylint:disable=invalid-name

    def __init__(self, hide_stdout):
        self.hide_stdout = hide_stdout

    def __enter__(self):
        if self.hide_stdout:
            self._streams = [sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__]
            sys.stdout, sys.stderr = DummyStream(), DummyStream()
            sys.__stdout__, sys.__stderr__ = DummyStream(), DummyStream()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hide_stdout:
            sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__ = self._streams
            del self._streams


class PylintTool(ToolBase):
    # There are several methods on this class which could technically
    # be functions (they don't use the 'self' argument) but that would
    # make this module/class a bit ugly.
    # pylint:disable=no-self-use

    def __init__(self):
        self._args = self._extra_sys_path = None
        self._collector = self._linter = None
        self._orig_sys_path = []
        self._streams = []
        self._hide_stdout = False

    def _prospector_configure(self, prospector_config, linter):
        linter.load_default_plugins()
        linter.load_plugin_modules(['pylint_common'])

        if 'django' in prospector_config.libraries:
            linter.load_plugin_modules(['pylint_django'])
        if 'celery' in prospector_config.libraries:
            linter.load_plugin_modules(['pylint_celery'])

        for msg_id in prospector_config.get_disabled_messages('pylint'):
            try:
                linter.disable(msg_id)
            # pylint: disable=pointless-except
            except UnknownMessage:
                # If the msg_id doesn't exist in PyLint any more,
                # don't worry about it.
                pass

        options = prospector_config.tool_options('pylint')

        for checker in linter.get_checkers():
            if not hasattr(checker, 'options'):
                continue
            for option in checker.options:
                if option[0] in options:
                    checker.set_option(option[0], options[option[0]])

        # The warnings about disabling warnings are useful for figuring out
        # with other tools to suppress messages from. For example, an unused
        # import which is disabled with 'pylint disable=unused-import' will still
        # generate an 'FL0001' unused import warning from pyflakes. Using the
        # information from these messages, we can figure out what was disabled.
        linter.disable('locally-disabled')  # notification about disabling a message
        linter.disable('locally-enabled')  # notification about enabling a message
        linter.enable('file-ignored')   # notification about disabling an entire file
        linter.enable('suppressed-message')   # notification about a message being supressed
        linter.disable('useless-suppression')  # notification about message supressed which was not raised
        linter.disable('deprecated-pragma')  # notification about use of deprecated 'pragma' option

        # disable the 'mixed indentation' warning, since it actually will only allow
        # the indentation specified in the pylint configuration file; we replace it
        # instead with our own version which is more lenient and configurable
        linter.disable('mixed-indentation')
        indent_checker = IndentChecker(linter)
        linter.register_checker(indent_checker)

        max_line_length = prospector_config.max_line_length
        for checker in linter.get_checkers():
            if not hasattr(checker, 'options'):
                continue
            for option in checker.options:
                if max_line_length is not None:
                    if option[0] == 'max-line-length':
                        checker.set_option('max-line-length', max_line_length)

    def _pylintrc_configure(self, pylintrc, linter):
        with stdout_wrapper(self._hide_stdout):
            linter.load_default_plugins()
            linter.load_file_configuration(pylintrc)

    def configure(self, prospector_config, found_files):

        extra_sys_path = found_files.get_minimal_syspath()
        self._hide_stdout = not prospector_config.loquacious_pylint

        # create a list of packages, but don't include packages which are
        # subpackages of others as checks will be duplicated
        packages = [p.split(os.path.sep) for p in found_files.iter_package_paths(abspath=False)]
        packages.sort(key=len)
        check_paths = set()
        for package in packages:
            package_path = os.path.join(*package)
            if len(package) == 1:
                check_paths.add(package_path)
                continue
            for i in range(1, len(package)):
                if os.path.join(*package[:-i]) in check_paths:
                    break
            else:
                check_paths.add(package_path)

        for filepath in found_files.iter_module_paths(abspath=False):
            package = os.path.dirname(filepath).split(os.path.sep)
            for i in range(0, len(package)):
                if os.path.join(*package[:i + 1]) in check_paths:
                    break
            else:
                check_paths.add(filepath)

        check_paths = [found_files.to_absolute_path(p) for p in check_paths]

        # insert the target path into the system path to get correct behaviour
        self._orig_sys_path = sys.path
        # note: we prepend, so that modules are preferentially found in the
        # path given as an argument. This prevents problems where we are
        # checking a module which is already on sys.path before this
        # manipulation - for example, if we are checking 'requests' in a local
        # checkout, but 'requests' is already installed system wide, pylint
        # will discover the system-wide modules first if the local checkout
        # does not appear first in the path
        sys.path = list(extra_sys_path) + sys.path

        ext_found = False
        configured_by = None

        linter = ProspectorLinter(found_files)
        if prospector_config.use_external_config('pylint'):
            # try to find a .pylintrc
            pylintrc = prospector_config.external_config_location('pylint')
            if pylintrc is None:
                pylintrc = find_pylintrc()
            if pylintrc is None:
                pylintrc_path = os.path.join(prospector_config.workdir, '.pylintrc')
                if os.path.exists(pylintrc_path):
                    pylintrc = pylintrc_path

            if pylintrc is not None:
                # load it!
                configured_by = pylintrc
                ext_found = True

                self._args = linter.load_command_line_configuration(check_paths)
                self._pylintrc_configure(pylintrc, linter)

        if not ext_found:
            linter.reset_options()
            self._args = linter.load_command_line_configuration(check_paths)
            self._prospector_configure(prospector_config, linter)

        # Pylint 1.4 introduced the idea of explicitly specifying which C-extensions
        # to load. This is because doing so allows them to execute any code whatsoever,
        # which is considered to be unsafe. The following option turns off this, allowing
        # any extension to load again, since any setup.py can execute arbitrary code and
        # the safety gained through this approach seems minimal. Leaving it on means
        # that the inference engine cannot do much inference on modules with C-extensions
        # which is a bit useless.
        linter.set_option('unsafe-load-any-extension', True)

        # we don't want similarity reports right now
        linter.disable('similarities')

        # use the collector 'reporter' to simply gather the messages
        # given by PyLint
        self._collector = Collector(linter.msgs_store)
        linter.set_reporter(self._collector)

        self._linter = linter
        return configured_by

    def _combine_w0614(self, messages):
        """
        For the "unused import from wildcard import" messages,
        we want to combine all warnings about the same line into a single message.
        """
        by_loc = defaultdict(list)
        out = []

        for message in messages:
            if message.code == 'unused-wildcard-import':
                by_loc[message.location].append(message)
            else:
                out.append(message)

        for location, message_list in by_loc.items():
            names = []
            for msg in message_list:
                names.append(_UNUSED_WILDCARD_IMPORT_RE.match(msg.message).group(1))

            msgtxt = 'Unused imports from wildcard import: %s' % ', '.join(names)
            combined_message = Message('pylint', 'unused-wildcard-import', location, msgtxt)
            out.append(combined_message)

        return out

    def combine(self, messages):
        """
        Some error messages are repeated, causing many errors where only one is strictly necessary.

        For example, having a wildcard import will result in one 'Unused Import' warning for every unused import.
        This method will combine these into a single warning.
        """
        combined = self._combine_w0614(messages)
        return sorted(combined)

    def run(self, found_files):
        # note: Pylint will exit with a status code indicating the health of
        # the code it was checking. Prospector will not mimic this behaviour,
        # as it interferes with scripts which depend on and expect the exit
        # code of the code checker to match whether the check itself was
        # successful.

        # Additionally, pylint has occasional print statements which can be triggered
        # in exceptional cases. If this happens, then the output formatting of
        # prospector will be broken (for example, JSON format). Therefore we will
        # override stdout to neutralise these errant statements.
        # For an example, see
        # https://bitbucket.org/logilab/pylint/src/3f8ededd0b1637396937da8fe136f51f2bafb047/checkers/variables.py?at=default#cl-617

        # TODO: it'd be nice in the future to do something with this data in case it's useful!

        with stdout_wrapper(self._hide_stdout):
            self._linter.check(self._args)
        sys.path = self._orig_sys_path

        messages = self._collector.get_messages()
        return self.combine(messages)
