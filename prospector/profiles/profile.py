# -*- coding: utf-8 -*-
import json
import os

import yaml
from prospector.tools import TOOLS

BUILTIN_PROFILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'profiles'))


class ProfileNotFound(Exception):
    def __init__(self, name, profile_path):
        super(ProfileNotFound, self).__init__()
        self.name = name
        self.profile_path = profile_path

    def __repr__(self):
        return "Could not find profile %s; searched in %s" % (self.name, ':'.join(self.profile_path))


class CannotParseProfile(Exception):
    def __init__(self, filepath, parse_error):
        super(CannotParseProfile, self).__init__()
        self.filepath = filepath
        self.parse_error = parse_error

    def get_parse_message(self):
        return '%s\n  on line %s : char %s' % (self.parse_error.problem,
                                               self.parse_error.problem_mark.line,
                                               self.parse_error.problem_mark.column)

    def __repr__(self):
        return "Could not parse profile found at %s - it is not valid YAML" % self.filepath


class ProspectorProfile(object):

    def __init__(self, name, profile_dict, inherit_order):
        self.name = name
        self.inherit_order = inherit_order

        self.ignore_paths = _ensure_list(profile_dict.get('ignore-paths', []))
        # The 'ignore' directive is an old one which should be deprecated at some point
        self.ignore_patterns = _ensure_list(
            profile_dict.get('ignore-patterns', []) + profile_dict.get('ignore', [])
        )

        self.output_format = profile_dict.get('output-format')
        self.output_target = profile_dict.get('output-target')
        self.autodetect = profile_dict.get('autodetect')
        self.uses = [uses for uses in _ensure_list(profile_dict.get('uses', []))
                     if uses in ('django', 'celery', 'flask')]
        self.max_line_length = profile_dict.get('max-line-length')

        # informational shorthands
        self.strictness = profile_dict.get('strictness')
        self.test_warnings = profile_dict.get('test-warnings')
        self.doc_warnings = profile_dict.get('doc-warnings')
        self.member_warnings = profile_dict.get('member-warnings')

        # TODO: this is needed by Landscape but not by prospector; there is probably a better place for it
        self.requirements = _ensure_list(profile_dict.get('requirements', []))
        self.python_targets = _ensure_list(profile_dict.get('python-targets', []))

        for tool in TOOLS.keys():
            conf = {
                'disable': [],
                'enable': [],
                'run': None,
                'options': {}
            }
            conf.update(profile_dict.get(tool, {}))

            if self.max_line_length is not None and tool in ('pylint', 'pep8'):
                conf['options']['max-line-length'] = self.max_line_length

            setattr(self, tool, conf)

    def get_disabled_messages(self, tool_name):
        disable = getattr(self, tool_name)['disable']
        enable = getattr(self, tool_name)['enable']
        return list(set(disable) - set(enable))

    def is_tool_enabled(self, name):
        return getattr(self, name).get('run')

    def list_profiles(self):
        # this profile is itself included
        return self.inherit_order

    def as_dict(self):
        out = {
            'ignore-paths': self.ignore_paths,
            'ignore-patterns': self.ignore_patterns,
            'output-format': self.output_format,
            'output-file': self.output_file,
            'autodetect': self.autodetect,
            'uses': self.uses,
            'max-line-length': self.max_line_length,
            'member-warnings': self.member_warnings,
            'doc-warnings': self.doc_warnings,
            'test-warnings': self.test_warnings,
            'strictness': self.strictness,
            'requirements': self.requirements,
            'python-targets': self.python_targets,
        }
        for tool in TOOLS.keys():
            out[tool] = getattr(self, tool)
        return out

    def as_json(self):
        return json.dumps(self.as_dict())

    def as_yaml(self):
        return yaml.safe_dump(self.as_dict())

    @staticmethod
    def load(name_or_path, profile_path, allow_shorthand=True, forced_inherits=None):
        # First simply load all of the profiles and those that it explicitly inherits from
        data, inherits = _load_and_merge(name_or_path, profile_path, allow_shorthand,
                                         forced_inherits=forced_inherits or [])
        return ProspectorProfile(name_or_path, data, inherits)


def _is_valid_extension(filename):
    ext = os.path.splitext(filename)[1]
    return ext in ('.yml', '.yaml')


def _load_content(name_or_path, profile_path):
    filename = None

    if _is_valid_extension(name_or_path):
        for path in profile_path:
            filepath = os.path.join(path, name_or_path)
            if os.path.exists(filepath):
                # this is a full path that we can load
                filename = filepath
                break

        if filename is None:
            raise ProfileNotFound(name_or_path, profile_path)
    else:
        for path in profile_path:
            for ext in ('yml', 'yaml'):
                filepath = os.path.join(path, '%s.%s' % (name_or_path, ext))
                if os.path.exists(filepath):
                    filename = filepath
                    break

        if filename is None:
            raise ProfileNotFound(name_or_path, profile_path)

    with open(filename) as fct:
        try:
            return yaml.safe_load(fct) or {}
        except yaml.parser.ParserError as parse_error:
            raise CannotParseProfile(filename, parse_error)


def _ensure_list(value):
    if isinstance(value, list):
        return value
    return [value]


def _simple_merge_dict(priority, base):
    out = dict(base.items())
    out.update(dict(priority.items()))
    return out


def _merge_tool_config(priority, base):
    out = dict(base.items())
    for key, value in priority.items():
        if key in ('run', 'full', 'none'):  # pep8 has extra 'full' and 'none' options
            out[key] = value
        elif key in ('options',):
            out[key] = _simple_merge_dict(value, base.get(key, {}))

    # anything enabled in the 'priority' dict is removed
    # from 'disabled' in the base dict and vice versa
    base_disabled = base.get('disable') or []
    base_enabled = base.get('enable') or []
    pri_disabled = priority.get('disable') or []
    pri_enabled = priority.get('enable') or []

    out['disable'] = list(set(pri_disabled) | (set(base_disabled) - set(pri_enabled)))
    out['enable'] = list(set(pri_enabled) | (set(base_enabled) - set(pri_disabled)))

    return out


def _merge_profile_dict(priority, base):
    # copy the base dict into our output
    out = dict(base.items())

    for key, value in priority.items():
        if key in ('strictness', 'doc-warnings', 'test-warnings', 'member-warnings',
                   'output-format', 'autodetect', 'max-line-length',):
            # some keys are simple values which are overwritten
            out[key] = value
        elif key in ('ignore', 'ignore-patterns', 'ignore-paths', 'uses',
                     'requirements', 'python-targets'):
            # some keys should be appended
            out[key] = _ensure_list(value) + _ensure_list(base.get(key, []))
        elif key in TOOLS.keys():
            # this is tool config!
            out[key] = _merge_tool_config(value, base.get(key, {}))

    return out


def _determine_strictness(profile_dict, inherits):
    for profile in inherits:
        if profile.startswith('strictness_'):
            return None, False

    strictness = profile_dict.get('strictness')
    if strictness is None:
        return None, False
    return ('strictness_%s' % strictness), True


def _determine_pep8(profile_dict):
    pep8 = profile_dict.get('pep8', {})
    if pep8.get('full', False):
        return 'full_pep8', True
    elif pep8.get('none', False):
        return 'no_pep8', True
    return None, False


def _determine_doc_warnings(profile_dict):
    doc_warnings = profile_dict.get('doc-warnings')
    if doc_warnings is None:
        return None, False
    return ('doc_warnings' if doc_warnings else 'no_doc_warnings'), True


def _determine_test_warnings(profile_dict):
    test_warnings = profile_dict.get('test-warnings')
    if test_warnings is None:
        return None, False
    return (None if test_warnings else 'no_test_warnings'), True


def _determine_member_warnings(profile_dict):
    member_warnings = profile_dict.get('member-warnings')
    if member_warnings is None:
        return None, False
    return ('member_warnings' if member_warnings else 'no_member_warnings'), True


def _determine_implicit_inherits(profile_dict, already_inherits, shorthands_found):
    # Note: the ordering is very important here - the earlier items
    # in the list have precedence over the later items. The point of
    # the doc/test/pep8 profiles is usually to restore items which were
    # turned off in the strictness profile, so they must appear first.
    implicit = [
        ('pep8', _determine_pep8(profile_dict)),
        ('docs', _determine_doc_warnings(profile_dict)),
        ('tests', _determine_test_warnings(profile_dict)),
        ('strictness', _determine_strictness(profile_dict, already_inherits)),
        ('members', _determine_member_warnings(profile_dict)),
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


def _append_profiles(name, profile_path, data, inherit_list, allow_shorthand=False):
    new_data, new_il, _ = _load_profile(name, profile_path, allow_shorthand=allow_shorthand)
    data.update(new_data)
    inherit_list += new_il
    return data, inherit_list


def _load_and_merge(name_or_path, profile_path, allow_shorthand=True, forced_inherits=None):
    # First simply load all of the profiles and those that it explicitly inherits from
    data, inherit_list, shorthands_found = _load_profile(name_or_path, profile_path,
                                                         allow_shorthand=allow_shorthand,
                                                         forced_inherits=forced_inherits or [])

    if allow_shorthand:
        if 'docs' not in shorthands_found:
            data, inherit_list = _append_profiles('no_doc_warnings', profile_path, data, inherit_list)

        if 'members' not in shorthands_found:
            data, inherit_list = _append_profiles('no_member_warnings', profile_path, data, inherit_list)

        if 'tests' not in shorthands_found:
            data, inherit_list = _append_profiles('no_test_warnings', profile_path, data, inherit_list)

        if 'strictness' not in shorthands_found:
            # if no strictness was specified, then we should manually insert the medium strictness
            for inherit in inherit_list:
                if inherit.startswith('strictness_'):
                    break
            else:
                data, inherit_list = _append_profiles('strictness_medium', profile_path, data, inherit_list)

    # Now we merge all of the values together, from 'right to left' (ie, from the
    # top of the inheritance tree to the bottom). This means that the lower down
    # values overwrite those from above, meaning that the initially provided profile
    # has precedence.
    merged = {}
    for name in inherit_list[::-1]:
        priority = data[name]
        merged = _merge_profile_dict(priority, merged)

    return merged, inherit_list


def _load_profile(name_or_path, profile_path, shorthands_found=None,
                  already_loaded=None, allow_shorthand=True, forced_inherits=None):
    # recursively get the contents of the basic profile and those it inherits from
    base_contents = _load_content(name_or_path, profile_path)

    inherit_order = [name_or_path]
    shorthands_found = shorthands_found or set()

    already_loaded = already_loaded or []
    already_loaded.append(name_or_path)

    inherits = _ensure_list(base_contents.get('inherits', []))
    if forced_inherits is not None:
        inherits += forced_inherits

    # There are some 'shorthand' options in profiles which implicitly mean that we
    # should inherit from some of prospector's built-in profiles
    if base_contents.get('allow-shorthand', True) and allow_shorthand:
        extra_inherits, extra_shorthands = _determine_implicit_inherits(base_contents, inherits, shorthands_found)
        inherits += extra_inherits
        shorthands_found |= extra_shorthands

    contents_dict = {name_or_path: base_contents}

    for inherit_profile in inherits:
        if inherit_profile in already_loaded:
            # we already have this loaded and in the list
            continue

        already_loaded.append(inherit_profile)
        new_cd, new_il, new_sh = _load_profile(inherit_profile, profile_path,
                                               shorthands_found, already_loaded, allow_shorthand)
        contents_dict.update(new_cd)
        inherit_order += new_il
        shorthands_found |= new_sh

    # note: a new list is returned here rather than simply using inherit_order to give astroid a
    # clue about the type of the returned object, as otherwise it can recurse infinitely and crash,
    # this meaning that prospector does not run on prospector cleanly!
    return contents_dict, list(inherit_order), shorthands_found
