import os
from pathlib import Path
from unittest import TestCase

from prospector.profiles.profile import ProspectorProfile

THIS_DIR = Path(__file__).parent
BUILTIN_PROFILES = THIS_DIR / "../../prospector/profiles/profiles"


class ProfileTestBase(TestCase):
    def setUp(self):
        self._profile_path = [str(THIS_DIR / "profiles"), str(BUILTIN_PROFILES)]


class TestOptionalProfiles(TestCase):
    def setUp(self) -> None:
        self._profile_path = [str(THIS_DIR / "profiles/test_optional"), str(BUILTIN_PROFILES)]

    def test_optional_missing(self):
        # just load it without an exception to verify that a missing inherits works fine
        profile = ProspectorProfile.load("optional_missing", self._profile_path)
        self.assertTrue(profile.is_tool_enabled("dodgy"))

    def test_optional_present(self):
        # just load it without an exception to verify that a missing inherits works fine
        profile = ProspectorProfile.load("optional_present", self._profile_path)
        self.assertFalse(profile.is_tool_enabled("dodgy"))


class TestToolRenaming(TestCase):
    def setUp(self) -> None:
        self._profile_path = [
            str(THIS_DIR / "profiles/renaming_pepX/test_inheritance"),
            str(THIS_DIR / "profiles/renaming_pepX"),
            str(BUILTIN_PROFILES),
        ]

    def test_old_inherits_from_new(self):
        profile = ProspectorProfile.load("child_oldname.yaml", self._profile_path, allow_shorthand=False)

        assert profile.is_tool_enabled("pydocstyle")
        assert profile.is_tool_enabled("pycodestyle")
        assert "D401" in profile.pydocstyle["enable"]
        assert "D401" not in profile.pydocstyle["disable"]

        assert "E266" not in profile.pycodestyle["disable"]

        assert 120 == profile.pycodestyle["options"]["max-line-length"]

    def test_new_inherits_from_old(self):
        """
        Ensure that `pep8` can inherit from a `pycodecstyle` block and vice versa
        """
        profile = ProspectorProfile.load("child_newname.yaml", self._profile_path, allow_shorthand=False)

        assert profile.is_tool_enabled("pydocstyle")
        assert profile.is_tool_enabled("pycodestyle")
        assert "D401" not in profile.pydocstyle["disable"]
        assert "D401" in profile.pydocstyle["enable"]

        assert "E266" not in profile.pycodestyle["disable"]

        assert 140 == profile.pycodestyle["options"]["max-line-length"]

    def test_legacy_names_equivalent(self):
        """
        'pep8' tool was renamed to pycodestyle, 'pep257' tool was renamed to pydocstyle

        This test is to ensure that, for backwards compatibility until it is removed in prospector 2.0,
        that the old names and the new names are equivalent in profiles
        """
        profile_old = ProspectorProfile.load("renaming_oldname", self._profile_path, allow_shorthand=False)
        profile_new = ProspectorProfile.load("renaming_newname", self._profile_path, allow_shorthand=False)

        # do they serialise to the same thing?
        for tool in ("pycodestyle", "pydocstyle"):
            old_dict = profile_old.as_dict()[tool]
            new_dict = profile_new.as_dict()[tool]
            self.assertListEqual(sorted(old_dict["disable"]), sorted(new_dict["disable"]))
            self.assertListEqual(sorted(old_dict["enable"]), sorted(new_dict["enable"]))
        self.assertDictEqual(profile_old.as_dict(), profile_new.as_dict())

        # do they have the same settings for everything?
        for prof in (profile_old, profile_new):
            self.assertTrue(prof.is_tool_enabled("pycodestyle"))
            self.assertTrue(prof.is_tool_enabled("pydocstyle"))
            self.assertEqual(prof.pycodestyle["options"]["max-line-length"], 120)

    def test_pep8_shorthand_with_newname(self):
        """
        'pep8' is still a valid entry in the profile but in the future, only as a shorthand ("pep8: full")
        however for now, it also has to be able to configure pycodestyle
        """
        profile = ProspectorProfile.load("pep8_shorthand_pycodestyle", self._profile_path, allow_shorthand=True)
        self.assertTrue("full_pep8" in profile.inherit_order)
        self.assertTrue(profile.is_tool_enabled("pycodestyle"))
        self.assertEqual(profile.pycodestyle["options"]["max-line-length"], 120)


class TestProfileParsing(ProfileTestBase):
    def test_empty_disable_list(self):
        """
        This test verifies that a profile can still be loaded if it contains
        an empty 'pylint.disable' list
        """
        profile = ProspectorProfile.load("empty_disable_list", self._profile_path, allow_shorthand=False)
        self.assertEqual([], profile.pylint["disable"])

    def test_empty_profile(self):
        """
        Verifies that a completely empty profile can still be parsed and have
        default values
        """
        profile = ProspectorProfile.load("empty_profile", self._profile_path, allow_shorthand=False)
        self.assertEqual([], profile.pylint["disable"])

    def test_ignores(self):
        profile = ProspectorProfile.load("ignores", self._profile_path)
        self.assertEqual(["^tests/", "/migrations/"].sort(), profile.ignore_patterns.sort())

    def test_disable_tool(self):
        profile = ProspectorProfile.load("pylint_disabled", self._profile_path)
        self.assertFalse(profile.is_tool_enabled("pylint"))
        self.assertTrue(profile.is_tool_enabled("pycodestyle"))

    def test_load_plugins(self):
        profile = ProspectorProfile.load("pylint_load_plugins", self._profile_path)
        self.assertEqual(["first_plugin", "second_plugin"], profile.pylint["load-plugins"])


class TestProfileInheritance(ProfileTestBase):
    def _example_path(self, testname):
        return os.path.join(os.path.dirname(__file__), "profiles", "inheritance", testname)

    def _load(self, testname):
        profile_path = self._profile_path + [self._example_path(testname)]
        return ProspectorProfile.load("start", profile_path)

    def test_simple_inheritance(self):
        profile = ProspectorProfile.load("inherittest3", self._profile_path, allow_shorthand=False)
        disable = profile.pylint["disable"]
        disable.sort()
        self.assertEqual(["I0002", "I0003", "raw-checker-failed"], disable)

    def test_disable_tool_inheritance(self):
        profile = ProspectorProfile.load("pydocstyle_and_pylint_disabled", self._profile_path)
        self.assertFalse(profile.is_tool_enabled("pylint"))
        self.assertFalse(profile.is_tool_enabled("pydocstyle"))

    def test_precedence(self):
        profile = self._load("precedence")
        self.assertTrue(profile.is_tool_enabled("pylint"))
        self.assertTrue("expression-not-assigned" in profile.get_disabled_messages("pylint"))

    def test_strictness_equivalence(self):
        profile = self._load("strictness_equivalence")
        medium_strictness = ProspectorProfile.load("strictness_medium", self._profile_path)
        self.assertListEqual(
            sorted(profile.pylint["disable"]),
            sorted(medium_strictness.pylint["disable"]),
        )

    def test_shorthand_inheritance(self):
        profile = self._load("shorthand_inheritance")
        high_strictness = ProspectorProfile.load(
            "strictness_high",
            self._profile_path,
            # don't implicitly add things
            allow_shorthand=False,
            # but do include the profiles that the start.yaml will
            forced_inherits=["doc_warnings", "no_member_warnings"],
        )
        self.assertDictEqual(profile.pylint, high_strictness.pylint)
        self.assertDictEqual(profile.pycodestyle, high_strictness.pycodestyle)
        self.assertDictEqual(profile.pyflakes, high_strictness.pyflakes)

    def test_tool_enabled(self):
        profile = self._load("tool_enabled")
        self.assertTrue(profile.is_tool_enabled("pydocstyle"))
        self.assertFalse(profile.is_tool_enabled("pylint"))

    def test_pycodestyle_inheritance(self):
        profile = self._load("pep8")
        self.assertTrue("full_pep8" in profile.inherit_order)
