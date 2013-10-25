from prospector.adaptor.base import AdaptorBase
from prospector.profiles.profile import load_profiles, merge_profiles
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
