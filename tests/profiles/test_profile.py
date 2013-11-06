import os
from unittest import TestCase
from prospector.profiles.profile import _merge_dict, merge_profiles, from_file, load_profiles


class TestProfileParsing(TestCase):

    def setUp(self):
        self._basedir = os.path.join(os.path.dirname(__file__), 'profiles')

    def _file_content(self, name):
        path = os.path.join(self._basedir, name)
        with open(path) as f:
            return f.read()

    def test_empty_disable_list(self):
        """
        This test verifies that a profile can still be loaded if it contains
        an empty 'pylint.disable' list
        """
        profile = load_profiles('empty_disable_list', basedir=self._basedir)
        self.assertEqual([], profile.pylint['disable'])

    def test_empty_profile(self):
        """
        Verifies that a completely empty profile can still be parsed and have
        default values
        """
        profile = load_profiles('empty_profile', basedir=self._basedir)
        self.assertEqual([], profile.pylint['disable'])

    def test_inheritance(self):
        profile = load_profiles('inherittest3', basedir=self._basedir)
        disable = profile.pylint['disable']
        disable.sort()
        self.assertEqual(['I0001', 'I0002', 'I0003'], disable)

    def test_profile_merge(self):

        profile1 = from_file('mergetest1', self._basedir)
        profile2 = from_file('mergetest2', self._basedir)
        profile3 = from_file('mergetest3', self._basedir)

        merged = merge_profiles((profile1, profile2, profile3))

        merged_disabled_warnings = merged.pylint['disable']
        merged_disabled_warnings.sort()
        expected = ['C1000', 'C1001', 'E0504', 'W1010', 'W1012']
        self.assertEqual(expected, merged_disabled_warnings)

    def test_ignores(self):
        profile = load_profiles('ignores', basedir=self._basedir)
        self.assertEqual(['^tests/', '/migrations/'].sort(), profile.ignore.sort())

    def test_dict_merge(self):
        a = {
            'int': 1,
            'str': 'fish',
            'list': [1, 2],
            'dict': {
                'a': 1,
                'b': 2
            }
        }
        b = {
            'int': 2,
            'list': [2, 3],
            'dict': {
                'a': 3,
                'c': 4
            }
        }

        expected = {
            'int': 2,
            'str': 'fish',
            'list': [1, 2, 3],
            'dict': {
                'a': 3,
                'b': 2,
                'c': 4
            }
        }
        self.assertEqual(expected, _merge_dict(a, b, dedup_lists=True, d1_priority=False))

        expected = {
            'int': 1,
            'str': 'fish',
            'list': [1, 2, 3],
            'dict': {
                'a': 1,
                'b': 2,
                'c': 4
            }
        }
        self.assertEqual(expected, _merge_dict(a, b, dedup_lists=True, d1_priority=True))