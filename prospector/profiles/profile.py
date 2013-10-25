import os
import yaml


_empty_data = {
    'inherits': [],
    'pylint': {
        'disable': [],
        'options': []
    }
}


def load_profiles(names, basedir=None):
    if not isinstance(names, (list, tuple)):
        names = (names,)
    profiles = [_load_profile(name, basedir=basedir)[0] for name in names]
    return merge_profiles(profiles)


def _load_profile(name, basedir=None, inherit_set=None):
    inherit_set = inherit_set or set()

    profile = from_file(name, basedir)
    inherit_set.add(profile.name)

    for inherited in profile.inherits:
        if inherited not in inherit_set:
            inherited_profile, sub_inherit_set = _load_profile(inherited, basedir, inherit_set)
            try:
                profile.merge(inherited_profile)
            except ValueError:
                import pdb; pdb.set_trace()
            inherit_set |= sub_inherit_set

    return profile, inherit_set


def from_file(profile_name, basedir=None):
    filename = '%s.yaml' % profile_name
    basedir = basedir or os.path.join(os.path.dirname(__file__), 'profiles')
    filepath = os.path.join(basedir, filename)
    with open(filepath) as f:
        return parse_profile(profile_name, f.read())


def parse_profile(name, contents):
    data = yaml.load(contents)
    if data is None:
        # this happens if a completely empty YAML file is passed in to parse_profile, for example
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
            raise ValueError("Could not merge conflicting types %s and %s" % (type(value), type(d1[key])))
        elif isinstance(value, dict):
            newdict[key] = _merge_dict(d1[key], value, dedup_lists, d1_priority)
        elif isinstance(value, (list, tuple)):
            newdict[key] = list(set(d1[key]) | set(value))
        elif not d1_priority:
            newdict[key] = value

    return newdict


class StrictnessProfile(object):

    def __init__(self, name, profile_dict):
        self.name = name
        self.pylint = profile_dict['pylint']
        self.inherits = profile_dict['inherits']

    def to_profile_dict(self):
        return {
            'inherits': self.inherits,
            'pylint': self.pylint
        }

    def merge(self, other_profile):
        self.inherits = list(set(self.inherits + other_profile.inherits))
        self.pylint = _merge_dict(self.pylint, other_profile.pylint)


def merge_profiles(profiles):
    merged_profile = profiles[0]
    for profile in profiles[1:]:
        merged_profile.merge(profile)
    return merged_profile
