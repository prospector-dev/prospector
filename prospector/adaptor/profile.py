from prospector.adaptor.base import AdaptorBase
from prospector.profiles.profile import load_profiles
from pylint.utils import UnknownMessage


class ProfileAdaptor(AdaptorBase):

    def __init__(self, profile_names):
        self.profile = load_profiles(profile_names)
        self.name = 'profiles:%s' % ','.join(profile_names)

    def adapt_pylint(self, linter):
        for msg_id in self.profile.pylint['disable']:
            try:
                linter.disable(msg_id)
            except UnknownMessage:
                pass

        options = self.profile.pylint['options']

        for checker in linter.get_checkers():
            if not hasattr(checker, 'options'):
                continue
            for option in checker.options:
                if option[0] in options:
                    checker.set_option(option[0], options[option[0]])

    def adapt_pyflakes(self, tool):
        tool.ignore_codes = tuple(set(
            tool.ignore_codes
            + tuple(self.profile.pyflakes['disable'])
        ))
