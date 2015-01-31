import os
from unittest import TestCase
from prospector.profiles.profile import ProspectorProfile


class ProfileTestBase(TestCase):

    def setUp(self):
        self._profile_path = [
            os.path.join(os.path.dirname(__file__), 'profiles'),
            os.path.join(os.path.dirname(__file__), '../../prospector/profiles/profiles')
        ]

    def _file_content(self, name):
        path = os.path.join(self._profile_path, name)
        with open(path) as f:
            return f.read()


class TestProfileParsing(ProfileTestBase):

    def test_empty_disable_list(self):
        """
        This test verifies that a profile can still be loaded if it contains
        an empty 'pylint.disable' list
        """
        profile = ProspectorProfile.load('empty_disable_list', self._profile_path, allow_shorthand=False)
        self.assertEqual([], profile.pylint['disable'])

    def test_empty_profile(self):
        """
        Verifies that a completely empty profile can still be parsed and have
        default values
        """
        profile = ProspectorProfile.load('empty_profile', self._profile_path, allow_shorthand=False)
        self.assertEqual([], profile.pylint['disable'])

    def test_ignores(self):
        profile = ProspectorProfile.load('ignores', self._profile_path)
        self.assertEqual(['^tests/', '/migrations/'].sort(), profile.ignore_patterns.sort())

    def test_disable_tool(self):
        profile = ProspectorProfile.load('pylint_disabled', self._profile_path)
        self.assertFalse(profile.is_tool_enabled('pylint'))
        self.assertTrue(profile.is_tool_enabled('pep8') is None)


class TestProfileInheritance(ProfileTestBase):

    def _example_path(self, testname):
        return os.path.join(os.path.dirname(__file__), 'profiles', 'inheritance', testname)

    def _load(self, testname):
        profile_path = self._profile_path + [self._example_path(testname)]
        return ProspectorProfile.load('start', profile_path)

    def test_simple_inheritance(self):
        profile = ProspectorProfile.load('inherittest3', self._profile_path, allow_shorthand=False)
        disable = profile.pylint['disable']
        disable.sort()
        self.assertEqual(['I0002', 'I0003', 'raw-checker-failed'], disable)

    def test_disable_tool_inheritance(self):
        profile = ProspectorProfile.load('pep8_and_pylint_disabled', self._profile_path)
        self.assertFalse(profile.is_tool_enabled('pylint'))
        self.assertFalse(profile.is_tool_enabled('pep8'))

    def test_precedence(self):
        profile = self._load('precedence')
        self.assertTrue(profile.is_tool_enabled('pylint'))
        self.assertTrue('expression-not-assigned' in profile.get_disabled_messages('pylint'))

    def test_strictness_equivalence(self):
        profile = self._load('strictness_equivalence')
        medium_strictness = ProspectorProfile.load('strictness_medium', self._profile_path)
        self.assertListEqual(sorted(profile.pylint['disable']), sorted(medium_strictness.pylint['disable']))

    def test_shorthand_inheritance(self):
        profile = self._load('shorthand_inheritance')
        high_strictness = ProspectorProfile.load('strictness_high', self._profile_path,
                                                 # don't implicitly add things
                                                 allow_shorthand=False,
                                                 # but do include the profiles that the start.yaml will
                                                 forced_inherits=['doc_warnings', 'no_member_warnings']
        )
        self.assertDictEqual(profile.pylint, high_strictness.pylint)
        self.assertDictEqual(profile.pep8, high_strictness.pep8)
        self.assertDictEqual(profile.pyflakes, high_strictness.pyflakes)

    def test_pep8_inheritance(self):
        profile = self._load('pep8')
        self.assertTrue(profile.is_tool_enabled('pep8'))
