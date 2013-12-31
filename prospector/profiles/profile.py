import os
import yaml


class ProfileNotFound(Exception):
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath

    def __repr__(self):
        return "Could not find profile %s at %s" % (self.name, self.filepath)


_empty_data = {
    'inherits': [],
    'pep8': {
        'disable': [],
        'options': {},
    },
    'pylint': {
        'disable': [],
        'options': {}
    },
    'ignore': [],
}


def load_profiles(names, basedir=None):
    if not isinstance(names, (list, tuple)):
        names = (names,)
    profiles = [_load_profile(name, basedir=basedir)[0] for name in names]
    return merge_profiles(profiles)


def _load_content(name, basedir=None):

    if name.endswith('.yaml'):
        # assume that this is a full path that we can load
        filename = name
    else:
        basedir = basedir or os.path.join(
            os.path.dirname(__file__),
            'profiles',
        )
        filename = os.path.join(basedir, '%s.yaml' % name)

    if not os.path.exists(filename):
        raise ProfileNotFound(name, os.path.abspath(filename))

    with open(filename) as f:
        return f.read()


def from_file(name, basedir=None):
    return parse_profile(name, _load_content(name, basedir))


def _load_profile(name, basedir=None, inherits_set=None):
    inherits_set = inherits_set or set()

    profile = parse_profile(name, _load_content(name, basedir))
    inherits_set.add(profile.name)

    for inheritsed in profile.inherits:
        if inheritsed not in inherits_set:
            inheritsed_profile, sub_inherits_set = _load_profile(
                inheritsed,
                basedir,
                inherits_set,
            )
            profile.merge(inheritsed_profile)
            inherits_set |= sub_inherits_set

    return profile, inherits_set


def parse_profile(name, contents):
    if name.endswith('.yaml'):
        # this was a full path
        name = os.path.splitext(os.path.basename(name))[0]
    data = yaml.load(contents)
    if data is None:
        # this happens if a completely empty YAML file is passed in to
        # parse_profile, for example
        data = dict(_empty_data)
    else:
        data = _merge_dict(_empty_data, data, d1_priority=False)
    return StrictnessProfile(name, data)


def _merge_dict(d1, d2, dedup_lists=False, d1_priority=True):
    newdict = {}
    newdict.update(d1)

    for key, value in d2.iteritems():
        if key not in d1:
            newdict[key] = value
        elif value is None and d1[key] is not None:
            newdict[key] = d1[key]
        elif d1[key] is None and value is not None:
            newdict[key] = value
        elif type(value) != type(d1[key]):
            raise ValueError("Could not merge conflicting types %s and %s" % (
                type(value),
                type(d1[key]),
            ))
        elif isinstance(value, dict):
            newdict[key] = _merge_dict(
                d1[key],
                value,
                dedup_lists,
                d1_priority,
            )
        elif isinstance(value, (list, tuple)):
            newdict[key] = list(set(d1[key]) | set(value))
        elif not d1_priority:
            newdict[key] = value

    return newdict


class StrictnessProfile(object):

    def __init__(self, name, profile_dict):
        self.name = name
        self.pep8 = profile_dict['pep8']
        self.pylint = profile_dict['pylint']
        self.inherits = profile_dict['inherits']
        self.ignore = profile_dict['ignore']

    def to_profile_dict(self):
        return {
            'inherits': self.inherits,
            'ignore': self.ignore,
            'pep8': self.pep8,
            'pylint': self.pylint
        }

    def merge(self, other_profile):
        self.ignore = list(set(self.ignore + other_profile.ignore))
        self.inherits = list(set(self.inherits + other_profile.inherits))
        self.pep8 = _merge_dict(self.pep8, other_profile.pep8)
        self.pylint = _merge_dict(self.pylint, other_profile.pylint)


def merge_profiles(profiles):
    merged_profile = profiles[0]
    for profile in profiles[1:]:
        merged_profile.merge(profile)
    return merged_profile
