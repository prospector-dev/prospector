from prospector.adaptor.base import AdaptorBase
from prospector.profiles.profile import load_profiles
from pylint.utils import UnknownMessage


class ProfileAdaptor(AdaptorBase):

    def __init__(self, profile_names, profile_path):
        self.profile = load_profiles(profile_names, profile_path)
        self.name = 'profiles:%s' % ','.join(profile_names)

    def is_tool_enabled(self, tool_name):
        return self.profile.is_tool_enabled(tool_name)

    def get_output_format(self):
        return self.profile.output_format

    def adapt_pylint(self, linter):
        disabled = self.profile.get_disabled_messages('pylint')

        for msg_id in disabled:
            try:
                linter.disable(msg_id)

            # pylint: disable=W0704
            except UnknownMessage:
                # If the msg_id doesn't exist in PyLint any more,
                # don't worry about it.
                pass

        options = self.profile.pylint['options']

        for checker in linter.get_checkers():
            if not hasattr(checker, 'options'):
                continue
            for option in checker.options:
                if option[0] in options:
                    checker.set_option(option[0], options[option[0]])

    def _simple_ignore(self, name, tool):
        disabled = self.profile.get_disabled_messages(name)
        tool.ignore_codes = tuple(set(
            tool.ignore_codes + tuple(disabled)
        ))

    def adapt_mccabe(self, tool):
        self._simple_ignore('mccabe', tool)

        if 'max-complexity' in self.profile.mccabe['options']:
            tool.max_complexity = \
                self.profile.mccabe['options']['max-complexity']

    def adapt_pyflakes(self, tool):
        self._simple_ignore('pyflakes', tool)

    def adapt_frosted(self, tool):
        self._simple_ignore('frosted', tool)

    def adapt_pep8(self, style_guide, use_config=True):
        if not use_config:
            return

        disabled = self.profile.get_disabled_messages('pep8')

        style_guide.options.ignore = tuple(set(
            style_guide.options.ignore + tuple(disabled)
        ))

        if 'max-line-length' in self.profile.pep8['options']:
            style_guide.options.max_line_length = \
                self.profile.pep8['options']['max-line-length']

    def adapt_pep257(self, tool):
        self._simple_ignore('pep257', tool)

    def adapt_pyroma(self, tool):
        self._simple_ignore('pyroma', tool)
