import re
import os
from pkg_resources import Requirement


_PIP_OPTIONS = (
    '-i', '--index-url',
    '--extra-index-url',
    '--no-index',
    '-f', '--find-links',
    '-r'
)


class DependenciesNotFoundException(Exception):
    pass


def find_dependencies(path):
    """
    This method tries to determine the dependencies of a particular project
    by inspecting the possible places that they could be defined.

    It will attempt, in order:

    1) to parse setup.py in the root for an install_requires value
    2) to read a requirements.txt file in the root
    3) to read all .txt files in a folder called 'requirements' in the root
    4) to read files matching "*requirements*.txt" and "*reqs*.txt" in the root,
       excluding any starting or ending with 'test'

    If one of these succeeds, then a list of pkg_resources.Requirement's
    will be returned. If none can be found, then a DependenciesNotFoundException
    will be raised
    """
    pass


def from_setup_py(setup_file):
    pass


def from_requirements_txt(requirements_file):
    # see http://www.pip-installer.org/en/latest/logic.html
    requirements = []
    with open(requirements_file) as f:
        for req in f.readlines():
            if req.strip() == '':
                # empty line
                continue
            if req.strip().startswith('#'):
                # this is a comment
                continue
            if req.strip().split()[0] in _PIP_OPTIONS:
                # this is a pip option
                continue
            if req.strip().startswith('-e'):
                # TODO: this should handle local/vcs dependencies too
                continue
            if any([req.strip().startswith(protocol) for protocol in ('http', 'https', 'ftp', 'sftp')]):
                # TODO: this should also deal with archive URLs
                continue
            requirements.append(Requirement.parse(req))

    requirements.sort(key=lambda r: r.key)
    return requirements


def from_requirements_dir(path):
    requirements = []
    for entry in os.listdir(path):
        filepath = os.path.join(path, entry)
        if os.path.isfile(filepath) and entry.endswith('.txt'):
            # TODO: deal with duplicates
            requirements += from_requirements_txt(filepath)

    requirements.sort(key=lambda r: r.key)
    return requirements


def from_requirements_blob(path):
    requirements = []

    for entry in os.listdir(path):
        filepath = os.path.join(path, entry)
        if not os.path.isfile(filepath):
            continue
        m = re.match(r'^(\w*)req(uirement)?s(\w*)\.txt$', entry)
        if m is None:
            continue
        if m.group(1).startswith('test') or m.group(3).endswith('test'):
            continue
        requirements += from_requirements_txt(filepath)

    requirements.sort(key=lambda r: r.key)
    return requirements