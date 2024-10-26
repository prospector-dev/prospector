import codecs
import json
import os
import pkgutil
from pathlib import Path
from typing import Any, Optional, Union

import yaml

from prospector.profiles.exceptions import CannotParseProfile, ProfileNotFound
from prospector.tools import DEFAULT_TOOLS, TOOLS

BUILTIN_PROFILE_PATH = (Path(__file__).parent / "profiles").absolute()


class ProspectorProfile:
    def __init__(self, name: str, profile_dict: dict[str, Any], inherit_order: list[str]) -> None:
        self.name = name
        self.inherit_order = inherit_order

        self.ignore_paths = _ensure_list(profile_dict.get("ignore-paths", []))
        # The 'ignore' directive is an old one which should be deprecated at some point
        self.ignore_patterns = _ensure_list(profile_dict.get("ignore-patterns", []) + profile_dict.get("ignore", []))

        self.output_format = profile_dict.get("output-format")
        self.output_target = profile_dict.get("output-target")
        self.autodetect = profile_dict.get("autodetect", True)
        self.uses = [
            uses for uses in _ensure_list(profile_dict.get("uses", [])) if uses in ("django", "celery", "flask")
        ]
        self.max_line_length = profile_dict.get("max-line-length")

        # informational shorthands
        self.strictness = profile_dict.get("strictness")
        self.test_warnings = profile_dict.get("test-warnings")
        self.doc_warnings = profile_dict.get("doc-warnings")
        self.member_warnings = profile_dict.get("member-warnings")

        # TODO: this is needed by Landscape but not by prospector; there is probably a better place for it
        self.requirements = _ensure_list(profile_dict.get("requirements", []))

        for tool in TOOLS:
            tool_conf = profile_dict.get(tool, {})

            # set the defaults for everything
            conf: dict[str, Any] = {"disable": [], "enable": [], "run": None, "options": {}}
            # use the "old" tool name
            conf.update(tool_conf)

            if self.max_line_length is not None and tool in ("pylint", "pycodestyle"):
                conf["options"]["max-line-length"] = self.max_line_length

            setattr(self, tool, conf)

    def get_disabled_messages(self, tool_name: str) -> list[str]:
        disable = getattr(self, tool_name)["disable"]
        enable = getattr(self, tool_name)["enable"]
        return list(set(disable) - set(enable))

    def get_enabled_messages(self, tool_name: str) -> list[str]:
        disable = getattr(self, tool_name)["disable"]
        enable = getattr(self, tool_name)["enable"]
        return list(set(enable) - set(disable))

    def is_tool_enabled(self, name: str) -> bool:
        enabled: Optional[bool] = getattr(self, name).get("run")
        if enabled is not None:
            return enabled
        # this is not explicitly enabled or disabled, so use the default
        return name in DEFAULT_TOOLS

    def list_profiles(self) -> list[str]:
        # this profile is itself included
        return [str(profile) for profile in self.inherit_order]

    def as_dict(self) -> dict[str, Any]:
        out = {
            "ignore-paths": self.ignore_paths,
            "ignore-patterns": self.ignore_patterns,
            "output-format": self.output_format,
            "output-target": self.output_target,
            "autodetect": self.autodetect,
            "uses": self.uses,
            "max-line-length": self.max_line_length,
            "member-warnings": self.member_warnings,
            "doc-warnings": self.doc_warnings,
            "test-warnings": self.test_warnings,
            "strictness": self.strictness,
            "requirements": self.requirements,
        }
        for tool in TOOLS:
            out[tool] = getattr(self, tool)
        return out

    def as_json(self) -> str:
        return json.dumps(self.as_dict())

    def as_yaml(self) -> str:
        return yaml.safe_dump(self.as_dict())

    @staticmethod
    def load(
        name_or_path: Union[str, Path],
        profile_path: list[Path],
        allow_shorthand: bool = True,
        forced_inherits: Optional[list[str]] = None,
    ) -> "ProspectorProfile":
        # First simply load all of the profiles and those that it explicitly inherits from
        data, inherits = _load_and_merge(
            name_or_path,
            profile_path,
            allow_shorthand,
            forced_inherits=forced_inherits or [],
        )
        return ProspectorProfile(str(name_or_path), data, inherits)


def _is_valid_extension(filename: Union[str, Path]) -> bool:
    ext = os.path.splitext(filename)[1]
    return ext in (".yml", ".yaml")


def _load_content_package(name: str) -> Optional[dict[str, Any]]:
    name_split = name.split(":", 1)
    module_name = f"prospector_profile_{name_split[0]}"
    file_names = (
        ["prospector.yaml", "prospector.yml"]
        if len(name_split) == 1
        else [f"{name_split[1]}.yaml", f"{name_split[1]}.yml"]
    )

    data = None
    used_name = None
    for file_name in file_names:
        used_name = f"{module_name}:{file_name}"
        data = pkgutil.get_data(module_name, file_name)
        if data is not None:
            break

    if data is None:
        return None

    try:
        return yaml.safe_load(data) or {}
    except yaml.parser.ParserError as parse_error:
        assert used_name is not None
        raise CannotParseProfile(used_name, parse_error) from parse_error


def _load_content(name_or_path: Union[str, Path], profile_path: list[Path]) -> dict[str, Any]:
    filename = None
    optional = False

    if isinstance(name_or_path, str) and name_or_path.endswith("?"):
        optional = True
        name_or_path = name_or_path[:-1]

    if _is_valid_extension(name_or_path):
        for path in profile_path:
            filepath = os.path.join(path, name_or_path)
            if os.path.exists(filepath):
                # this is a full path that we can load
                filename = filepath
                break
    else:
        for path in profile_path:
            for ext in ("yml", "yaml"):
                filepath = os.path.join(path, f"{name_or_path}.{ext}")
                if os.path.exists(filepath):
                    filename = filepath
                    break

    if filename is None:
        result = _load_content_package(str(name_or_path))
        if result is not None:
            return result

        if optional:
            return {}

        raise ProfileNotFound(str(name_or_path), profile_path)

    with codecs.open(filename) as fct:
        try:
            return yaml.safe_load(fct) or {}
        except yaml.parser.ParserError as parse_error:
            raise CannotParseProfile(filename, parse_error) from parse_error


def _ensure_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return [value]


def _simple_merge_dict(priority: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    out = {**base, **priority}
    keys = set(priority.keys()) | set(base.keys())
    for key in keys:
        if isinstance(base.get(key), dict) and isinstance(priority.get(key), dict):
            out[key] = _simple_merge_dict(priority[key], base[key])
    return out


def _merge_tool_config(priority: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    out = {**base, **priority}

    # add options that are missing, but keep existing options from the priority dictionary
    # TODO: write a unit test for this :-|
    out["options"] = _simple_merge_dict(priority.get("options", {}), base.get("options", {}))

    # anything enabled in the 'priority' dict is removed
    # from 'disabled' in the base dict and vice versa
    base_disabled: list[Any] = base.get("disable") or []
    base_enabled: list[Any] = base.get("enable") or []
    pri_disabled: list[Any] = priority.get("disable") or []
    pri_enabled: list[Any] = priority.get("enable") or []

    out["disable"] = list(set(pri_disabled) | (set(base_disabled) - set(pri_enabled)))
    out["enable"] = list(set(pri_enabled) | (set(base_enabled) - set(pri_disabled)))

    return out


def _merge_profile_dict(priority: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    # copy the base dict into our output
    out = dict(base.items())

    for key, value in priority.items():
        if key in (
            "strictness",
            "doc-warnings",
            "test-warnings",
            "member-warnings",
            "output-format",
            "autodetect",
            "max-line-length",
            "pep8",
        ):
            # some keys are simple values which are overwritten
            out[key] = value
        elif key in (
            "ignore",
            "ignore-patterns",
            "ignore-paths",
            "uses",
            "requirements",
            "python-targets",
            "output-target",
        ):
            # some keys should be appended
            out[key] = _ensure_list(value) + _ensure_list(base.get(key, []))
        elif key in TOOLS:
            # this is tool config!
            out[key] = _merge_tool_config(value, base.get(key, {}))

    return out


def _determine_strictness(profile_dict: dict[str, Any], inherits: list[str]) -> tuple[Optional[str], bool]:
    for profile in inherits:
        if profile.startswith("strictness_"):
            return None, False

    strictness = profile_dict.get("strictness")
    if strictness is None:
        return None, False
    return (f"strictness_{strictness}"), True


def _determine_pep8(profile_dict: dict[str, Any]) -> tuple[Optional[str], bool]:
    pep8 = profile_dict.get("pep8")
    if pep8 == "full":
        return "full_pep8", True
    if pep8 == "none":
        return "no_pep8", True
    if isinstance(pep8, dict) and pep8.get("full", False):
        return "full_pep8", False
    return None, False


def _determine_doc_warnings(profile_dict: dict[str, Any]) -> tuple[Optional[str], bool]:
    doc_warnings = profile_dict.get("doc-warnings")
    if doc_warnings is None:
        return None, False
    return ("doc_warnings" if doc_warnings else "no_doc_warnings"), True


def _determine_test_warnings(profile_dict: dict[str, Any]) -> tuple[Optional[str], bool]:
    test_warnings = profile_dict.get("test-warnings")
    if test_warnings is None:
        return None, False
    return (None if test_warnings else "no_test_warnings"), True


def _determine_member_warnings(profile_dict: dict[str, Any]) -> tuple[Optional[str], bool]:
    member_warnings = profile_dict.get("member-warnings")
    if member_warnings is None:
        return None, False
    return ("member_warnings" if member_warnings else "no_member_warnings"), True


def _determine_implicit_inherits(
    profile_dict: dict[str, Any], already_inherits: list[str], shorthands_found: set[str]
) -> tuple[list[str], set[str]]:
    # Note: the ordering is very important here - the earlier items
    # in the list have precedence over the later items. The point of
    # the doc/test/pep8 profiles is usually to restore items which were
    # turned off in the strictness profile, so they must appear first.
    implicit = [
        ("pep8", _determine_pep8(profile_dict)),
        ("docs", _determine_doc_warnings(profile_dict)),
        ("tests", _determine_test_warnings(profile_dict)),
        ("strictness", _determine_strictness(profile_dict, already_inherits)),
        ("members", _determine_member_warnings(profile_dict)),
    ]
    inherits = []

    for shorthand_name, determined in implicit:
        if shorthand_name in shorthands_found:
            continue
        extra_inherits, shorthand_found = determined
        if not shorthand_found:
            continue
        shorthands_found.add(shorthand_name)
        if extra_inherits is not None:
            inherits.append(extra_inherits)

    return inherits, shorthands_found


def _append_profiles(
    name: str,
    profile_path: list[Path],
    data: dict[Union[str, Path], Any],
    inherit_list: list[str],
    allow_shorthand: bool = False,
) -> tuple[dict[Union[str, Path], Any], list[str]]:
    new_data, new_il, _ = _load_profile(name, profile_path, allow_shorthand=allow_shorthand)
    data.update(new_data)
    inherit_list += new_il
    return data, inherit_list


def _load_and_merge(
    name_or_path: Union[str, Path],
    profile_path: list[Path],
    allow_shorthand: bool = True,
    forced_inherits: Optional[list[str]] = None,
) -> tuple[dict[str, Any], list[str]]:
    # First simply load all of the profiles and those that it explicitly inherits from
    data, inherit_list, shorthands_found = _load_profile(
        str(name_or_path),
        profile_path,
        allow_shorthand=allow_shorthand,
        forced_inherits=forced_inherits or [],
    )

    if allow_shorthand:
        if "docs" not in shorthands_found:
            data, inherit_list = _append_profiles("no_doc_warnings", profile_path, data, inherit_list)

        if "members" not in shorthands_found:
            data, inherit_list = _append_profiles("no_member_warnings", profile_path, data, inherit_list)

        if "tests" not in shorthands_found:
            data, inherit_list = _append_profiles("no_test_warnings", profile_path, data, inherit_list)

        if "strictness" not in shorthands_found:
            # if no strictness was specified, then we should manually insert the medium strictness
            for inherit in inherit_list:
                if inherit.startswith("strictness_"):
                    break
            else:
                data, inherit_list = _append_profiles("strictness_medium", profile_path, data, inherit_list)

    # Now we merge all of the values together, from 'right to left' (ie, from the
    # top of the inheritance tree to the bottom). This means that the lower down
    # values overwrite those from above, meaning that the initially provided profile
    # has precedence.
    merged: dict[str, Any] = {}
    for name in inherit_list[::-1]:
        priority = data[name]
        merged = _merge_profile_dict(priority, merged)

    return merged, inherit_list


def _transform_legacy(profile_dict: dict[str, Any]) -> dict[str, Any]:
    """
    After pep8 was renamed to pycodestyle, this pre-filter just moves profile
    config blocks using the old name to use the new name, merging if both are
    specified.

    Same for pep257->pydocstyle
    """
    out = {}

    # copy in existing pep8/pep257 using new names to start
    if "pycodestyle" in profile_dict:
        out["pycodestyle"] = profile_dict["pycodestyle"]
    if "pydocstyle" in profile_dict:
        out["pydocstyle"] = profile_dict["pydocstyle"]

    # pep8 is tricky as it's overloaded as a tool configuration and a shorthand
    # first, is this the short "pep8: full" version or a configuration of the
    # pycodestyle tool using the old name?
    if "pep8" in profile_dict:
        pep8conf = profile_dict["pep8"]
        if isinstance(pep8conf, dict):
            # merge in with existing config if there is any
            out["pycodestyle"] = _simple_merge_dict(out.get("pycodestyle", {}), pep8conf)
        else:
            # otherwise it's shortform, just copy it in directly
            out["pep8"] = pep8conf
        del profile_dict["pep8"]

    if "pep257" in profile_dict:
        out["pydocstyle"] = _simple_merge_dict(out.get("pydocstyle", {}), profile_dict["pep257"])
        del profile_dict["pep257"]

    # now just copy the rest in
    for key, value in profile_dict.items():
        if key in ("pycodestyle", "pydocstyle"):
            # already handled these
            continue
        out[key] = value

    return out


def _load_profile(
    name_or_path: Union[str, Path],
    profile_path: list[Path],
    shorthands_found: Optional[set[str]] = None,
    already_loaded: Optional[list[Union[str, Path]]] = None,
    allow_shorthand: bool = True,
    forced_inherits: Optional[list[str]] = None,
) -> tuple[dict[Union[str, Path], Any], list[str], set[str]]:
    # recursively get the contents of the basic profile and those it inherits from
    base_contents = _load_content(name_or_path, profile_path)

    base_contents = _transform_legacy(base_contents)

    inherit_order = [str(name_or_path)]
    shorthands_found = shorthands_found or set()

    already_loaded = already_loaded or []
    already_loaded.append(name_or_path)

    inherits = _ensure_list(base_contents.get("inherits", []))
    if forced_inherits is not None:
        inherits += forced_inherits

    # There are some 'shorthand' options in profiles which implicitly mean that we
    # should inherit from some of prospector's built-in profiles
    if base_contents.get("allow-shorthand", True) and allow_shorthand:
        extra_inherits, extra_shorthands = _determine_implicit_inherits(base_contents, inherits, shorthands_found)
        inherits += extra_inherits
        shorthands_found |= extra_shorthands

    contents_dict: dict[Union[str, Path], Any] = {name_or_path: base_contents}

    for inherit_profile in inherits:
        if inherit_profile in already_loaded:
            # we already have this loaded and in the list
            continue

        already_loaded.append(inherit_profile)
        new_cd, new_il, new_sh = _load_profile(
            inherit_profile,
            profile_path,
            shorthands_found,
            already_loaded,
            allow_shorthand,
        )
        contents_dict.update(new_cd)
        inherit_order += new_il
        shorthands_found |= new_sh

    # note: a new list is returned here rather than simply using inherit_order to give astroid a
    # clue about the type of the returned object, as otherwise it can recurse infinitely and crash,
    # this meaning that prospector does not run on prospector cleanly!
    return contents_dict, inherit_order, shorthands_found
