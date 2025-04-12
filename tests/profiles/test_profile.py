from pathlib import Path
from unittest import TestCase

import pytest

from prospector.profiles.exceptions import ProfileNotFound
from prospector.profiles.profile import ProspectorProfile

THIS_DIR = Path(__file__).parent
BUILTIN_PROFILES = THIS_DIR / "../../prospector/profiles/profiles"


class ProfileTestBase(TestCase):
    def setUp(self) -> None:
        self._profile_path = [THIS_DIR / "profiles", BUILTIN_PROFILES]


class TestOptionalProfiles(TestCase):
    def setUp(self) -> None:
        self._profile_path = [THIS_DIR / "profiles/test_optional", BUILTIN_PROFILES]

    def test_nonoptional_missing(self) -> None:
        with pytest.raises(ProfileNotFound):
            ProspectorProfile.load("nonoptional_missing", self._profile_path)

    def test_optional_missing(self) -> None:
        # ensure loads without an exception to verify that a missing inherits works fine
        profile = ProspectorProfile.load("optional_missing", self._profile_path)
        assert profile.is_tool_enabled("dodgy")

    def test_optional_present(self) -> None:
        # optional does not mean ignore so verify that values are inherited if present
        profile = ProspectorProfile.load("optional_present", self._profile_path)
        assert not profile.is_tool_enabled("dodgy")


class TestToolRenaming(TestCase):
    def setUp(self) -> None:
        self._profile_path = [
            THIS_DIR / "profiles/renaming_pepX/test_inheritance",
            THIS_DIR / "profiles/renaming_pepX",
            BUILTIN_PROFILES,
        ]

    def test_old_inherits_from_new(self) -> None:
        profile = ProspectorProfile.load("child_oldname.yaml", self._profile_path, allow_shorthand=False)

        assert profile.is_tool_enabled("pydocstyle")
        assert profile.is_tool_enabled("pycodestyle")
        assert "D401" in profile.pydocstyle["enable"]  # type: ignore[attr-defined]
        assert "D401" not in profile.pydocstyle["disable"]  # type: ignore[attr-defined]

        assert "E266" not in profile.pycodestyle["disable"]  # type: ignore[attr-defined]

        assert profile.pycodestyle["options"]["max-line-length"] == 120  # type: ignore[attr-defined]

    def test_new_inherits_from_old(self) -> None:
        """
        Ensure that `pep8` can inherit from a `pycodecstyle` block and vice versa
        """
        profile = ProspectorProfile.load("child_newname.yaml", self._profile_path, allow_shorthand=False)

        assert profile.is_tool_enabled("pydocstyle")
        assert profile.is_tool_enabled("pycodestyle")
        assert "D401" not in profile.pydocstyle["disable"]  # type: ignore[attr-defined]
        assert "D401" in profile.pydocstyle["enable"]  # type: ignore[attr-defined]

        assert "E266" not in profile.pycodestyle["disable"]  # type: ignore[attr-defined]

        assert profile.pycodestyle["options"]["max-line-length"] == 140  # type: ignore[attr-defined]

    def test_legacy_names_equivalent(self) -> None:
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
            assert sorted(old_dict["disable"]) == sorted(new_dict["disable"])
            assert sorted(old_dict["enable"]) == sorted(new_dict["enable"])
        assert profile_old.as_dict() == profile_new.as_dict()

        # do they have the same settings for everything?
        for prof in (profile_old, profile_new):
            assert prof.is_tool_enabled("pycodestyle")
            assert prof.is_tool_enabled("pydocstyle")
            assert prof.pycodestyle["options"]["max-line-length"] == 120  # type: ignore[attr-defined]

    def test_pep8_shorthand_with_newname(self) -> None:
        """
        'pep8' is still a valid entry in the profile but in the future, only as a shorthand ("pep8: full")
        however for now, it also has to be able to configure pycodestyle
        """
        profile = ProspectorProfile.load("pep8_shorthand_pycodestyle", self._profile_path, allow_shorthand=True)
        assert "full_pep8" in profile.inherit_order
        assert profile.is_tool_enabled("pycodestyle")
        assert profile.pycodestyle["options"]["max-line-length"] == 120  # type: ignore[attr-defined]


class TestProfileParsing(ProfileTestBase):
    def test_empty_disable_list(self) -> None:
        """
        This test verifies that a profile can still be loaded if it contains
        an empty 'pylint.disable' list
        """
        profile = ProspectorProfile.load("empty_disable_list", self._profile_path, allow_shorthand=False)
        assert profile.pylint["disable"] == []  # type: ignore[attr-defined]

    def test_empty_profile(self) -> None:
        """
        Verifies that a completely empty profile can still be parsed and have
        default values
        """
        profile = ProspectorProfile.load("empty_profile", self._profile_path, allow_shorthand=False)
        assert profile.pylint["disable"] == []  # type: ignore[attr-defined]

    def test_ignores(self) -> None:
        profile = ProspectorProfile.load("ignores", self._profile_path)
        assert sorted(["^tests/", "/migrations/"]) == sorted(profile.ignore_patterns)

    def test_enabled_in_disabled(self) -> None:
        """
        If a
        :return:
        """

    def test_disable_tool(self) -> None:
        profile = ProspectorProfile.load("pylint_disabled", self._profile_path)
        assert not profile.is_tool_enabled("pylint")
        assert profile.is_tool_enabled("pycodestyle")

    def test_load_plugins(self) -> None:
        profile = ProspectorProfile.load("pylint_load_plugins", self._profile_path)
        assert profile.pylint["load-plugins"] == ["first_plugin", "second_plugin"]  # type: ignore[attr-defined]


class TestProfileInheritance(ProfileTestBase):
    def _example_path(self, testname: str) -> Path:
        return Path(__file__).parent / "profiles" / "inheritance" / testname

    def _load(self, testname: str) -> ProspectorProfile:
        profile_path = self._profile_path + [self._example_path(testname)]
        return ProspectorProfile.load("start", profile_path)

    def test_simple_inheritance(self) -> None:
        profile = ProspectorProfile.load("inherittest3", self._profile_path, allow_shorthand=False)
        disable = profile.pylint["disable"]  # type: ignore[attr-defined]
        disable.sort()
        assert disable == ["I0002", "I0003", "raw-checker-failed"]

    def test_disable_tool_inheritance(self) -> None:
        profile = ProspectorProfile.load("pydocstyle_and_pylint_disabled", self._profile_path)
        assert not profile.is_tool_enabled("pylint")
        assert not profile.is_tool_enabled("pydocstyle")

    def test_precedence(self) -> None:
        profile = self._load("precedence")
        assert profile.is_tool_enabled("pylint")
        assert "expression-not-assigned" in profile.get_disabled_messages("pylint")

        # TODO: this doesn't work entirely as expected, but changing would be a backwards incompatible
        #       change - so this is parked until version 2.0

    #        self.assertFalse("D401" in profile.get_disabled_messages("pydocstyle"))

    def test_strictness_equivalence(self) -> None:
        profile = self._load("strictness_equivalence")
        medium_strictness = ProspectorProfile.load("strictness_medium", self._profile_path)
        assert (
            sorted(profile.pylint["disable"])  # type: ignore[attr-defined]
            == sorted(medium_strictness.pylint["disable"])  # type: ignore[attr-defined]
        )

    def test_shorthand_inheritance(self) -> None:
        profile = self._load("shorthand_inheritance")
        high_strictness = ProspectorProfile.load(
            "strictness_high",
            self._profile_path,
            # don't implicitly add things
            allow_shorthand=False,
            # but do include the profiles that the start.yaml will
            forced_inherits=["doc_warnings", "no_member_warnings"],
        )
        assert profile.pylint == high_strictness.pylint  # type: ignore[attr-defined]
        assert profile.pycodestyle == high_strictness.pycodestyle  # type: ignore[attr-defined]
        assert profile.pyflakes == high_strictness.pyflakes  # type: ignore[attr-defined]

    def test_tool_enabled(self) -> None:
        profile = self._load("tool_enabled")
        assert profile.is_tool_enabled("pydocstyle")
        assert not profile.is_tool_enabled("pylint")

    def test_pycodestyle_inheritance(self) -> None:
        profile = self._load("pep8")
        assert "full_pep8" in profile.inherit_order

    def test_module_inheritance(self) -> None:
        profile = ProspectorProfile.load("inherittest-module", self._profile_path, allow_shorthand=False)
        assert profile.pylint["disable"] == ["test-from-module"]  # type: ignore[attr-defined]

    def test_module_file_inheritance(self) -> None:
        profile = ProspectorProfile.load("inherittest-module-file", self._profile_path, allow_shorthand=False)
        assert profile.pylint["disable"] == ["alternate-test-from-module"]  # type: ignore[attr-defined]
