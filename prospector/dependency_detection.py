from astroid import MANAGER, CallFunc, Name, Assign, Keyword, List, Tuple, Const
import re
import os
from pkg_resources import Requirement


__all__ = ['find_dependencies',
           'DependenciesNotFoundException',
           'CouldNotParseDependencies']


_PIP_OPTIONS = (
    '-i', '--index-url',
    '--extra-index-url',
    '--no-index',
    '-f', '--find-links',
    '-r'
)


class DependenciesNotFoundException(Exception):
    pass


class CouldNotParseDependencies(Exception):
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


class SetupWalker(object):

    def __init__(self, ast):
        self._ast = ast
        self._setup_call = None
        self._top_level_assigns = {}
        self.walk()

    def walk(self, node=None):
        top = node is None
        node = node or self._ast

        # test to see if this is a call to setup()
        if isinstance(node, CallFunc):
            for child_node in node.get_children():
                if isinstance(child_node, Name) and child_node.name == 'setup':
                    # TODO: what if this isn't actually the distutils setup?
                    self._setup_call = node

        for child_node in node.get_children():
            if top and isinstance(child_node, Assign):
                for target in child_node.targets:
                    self._top_level_assigns[target.name] = child_node.value
            self.walk(child_node)

    def _get_list_value(self, list_node):
        values = []
        for child_node in list_node.get_children():
            if not isinstance(child_node, Const):
                # we can't handle anything fancy, only constant values
                raise CouldNotParseDependencies
            values.append(child_node.value)
        return values

    def get_install_requires(self):
        # first, if we have a call to setup, then we can see what its "install_requires" argument is
        if not self._setup_call:
            raise CouldNotParseDependencies

        for child_node in self._setup_call.get_children():
            if not isinstance(child_node, Keyword):
                # do we want to try to handle positional arguments?
                continue

            if child_node.arg != 'install_requires':
                continue

            if isinstance(child_node.value, (List, Tuple)):
                # joy! this is a simple list or tuple of requirements
                # this is a Keyword -> List or Keyword -> Tuple
                return self._get_list_value(child_node.value)

            if isinstance(child_node.value, Name):
                # otherwise, it's referencing a value defined elsewhere
                # this will be a Keyword -> Name
                try:
                    reqs = self._top_level_assigns[child_node.value.name]
                except KeyError:
                    raise CouldNotParseDependencies
                else:
                    if isinstance(reqs, (List, Tuple)):
                        return self._get_list_value(reqs)

            # otherwise it's something funky and we can't handle it
            raise CouldNotParseDependencies


def from_setup_py(setup_file):
    ast = MANAGER.ast_from_file(setup_file)
    walker = SetupWalker(ast)

    requirements = []
    for req in walker.get_install_requires():
        requirements.append(Requirement.parse(req))

    requirements.sort(key=lambda r: r.key)
    return requirements


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