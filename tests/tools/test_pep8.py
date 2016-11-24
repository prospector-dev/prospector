import os
import tempfile
from unittest import TestCase
from prospector.finder import find_python
from prospector.tools.pep8 import Pep8Tool


# A very basic stub to avoid creating a real ProspectorConfig, which wants
# command line (sys.argv) args and whatnot.
# Needed for handing to the Pep8Tool.configure(...) method, should expose the
# ProspectorConfig interface accessed in this method.
class StubProspectorConfig:
    # not actually used for anything here, default to s.th. "big"
    _max_line_length = 300

    def __init__(self, external_config=None):
        # external_config: optional file path to pep8/pycodestyle config file
        self.external_config = external_config

    @property
    def max_line_length(self):
        return self._max_line_length

    def use_external_config(self, _):
        return True

    def external_config_location(self, tool_name):
        return self.external_config

    def get_disabled_messages(self, tool_name):
        return []

    def tool_options(self, tool_name):
        return {}


# helper function
def rooted(root, paths):
    """Return list of paths with root dir prepended to each path."""
    return [os.path.normpath(os.path.join(root, p)) for p in paths]


class TestProspectorStyleGuidePathConfig(TestCase):
    # Test how prospector sets up the pep8/pycodestyle tool with regard to the
    # paths to check.
    # We need to create the ProspectorStyleGuide through a Pep8Tool instance
    # and use finder.find_python to create the input for Pep8Tool.configure()
    def _setup_styleguide(self, paths, external_config=None):
        # A helper to create the StyleGuide object.
        # root: the root directory for the relative paths given in the paths
        # and expected parameters
        pep8tool = Pep8Tool()
        config = StubProspectorConfig(external_config=external_config)
        found_python = find_python(
            ignores=[], paths=paths,
            explicit_file_mode=True if len(paths)>1 else False)

        configured_by, _ = pep8tool.configure(config, found_python)
        if external_config is not None:
            expected_configuration_message = (
                "Configuration found at %s" % external_config)
            self.assertEqual(configured_by, expected_configuration_message) 
        prospector_styleguide = pep8tool.checker
        return prospector_styleguide

    def test_paths_dir_arg(self):
        # test corresponding to a single command line PATH dir arg
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        # use the root directory itself as find_python input arg:
        paths = rooted(root, [''])
        # all Python modules in the directory tree are expected (but nothing 
        # else)
        expected = rooted(
            root,
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module.py',
             # 'package/subpackage/subpackage_plain.txt',
             'package/package_module.py',
             # 'package/package_plain.txt',
             'nonpackage/nonpackage_module.py',
             # 'nonpackage/nonpackage_plain.txt',
             'module.py',
             # 'plain.txt',
             ])
        expected = rooted(
            root,
            ['package',
             'package/subpackage',
             ])
        prospector_styleguide = self._setup_styleguide(paths)
        self.assertEqual(sorted(prospector_styleguide.paths), sorted(expected))

    def test_paths_dir_arg_pep8_exclude_cfg(self):
        # test corresponding to a single command line PATH dir arg, with
        # external pep8/pycodestyle config file
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        # use the root directory itself as find_python input arg:
        paths = rooted(root, [''])

        # set pep8/pycodestyle exclude config option
        external_config_contents = """
[pep8]
exclude = subpackage
        """
        expected = rooted(
            root,
            ['package',
             ])
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(external_config_contents)
            f.flush()
            prospector_styleguide = self._setup_styleguide(
                paths, external_config=f.name)
            # exclusion of paths happens when pydodestyle checking is actually
            # run, simulate this by using the .excluded() method
            paths_after_exclusion = [
                p for p in prospector_styleguide.paths 
                if not prospector_styleguide.excluded(p)]
            self.assertEqual(
                sorted(paths_after_exclusion), sorted(expected))

    def test_paths_py_modules_arg(self):
        # test corresponding to multiple Python module files PATHs args
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        paths = rooted(
            root,
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module.py',
             'package/package_module.py',
             'nonpackage/nonpackage_module.py',
             'module.py',
             ])

        # all Python modules given as paths args are expected (but nothing 
        # else)
        expected = rooted(
            root,
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module.py',
             'package/package_module.py',
             'nonpackage/nonpackage_module.py',
             'module.py',
             ])
        prospector_styleguide = self._setup_styleguide(paths)
        self.assertEqual(sorted(prospector_styleguide.paths), sorted(expected))

    def test_paths_files_arg(self):
        # test corresponding to multiple files PATHs args (Python modules and
        # other files)
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        paths = rooted(
            root,
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module.py',
             'package/subpackage/subpackage_plain.txt',
             'package/package_module.py',
             'package/package_plain.txt',
             'nonpackage/nonpackage_module.py',
             'nonpackage/nonpackage_plain.txt',
             'module.py',
             'plain.txt',
             ])

        # all files given as path args are expected (but nothing 
        # else)
        # TODO: Is this how it should work? Should the tools cater for
        # TODO: filtering non-Python files?
        expected = rooted(
            root,
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module.py',
             'package/subpackage/subpackage_plain.txt',
             'package/package_module.py',
             'package/package_plain.txt',
             'nonpackage/nonpackage_module.py',
             'nonpackage/nonpackage_plain.txt',
             'module.py',
             'plain.txt',
             ])
        prospector_styleguide = self._setup_styleguide(paths)
        self.assertEqual(sorted(prospector_styleguide.paths), sorted(expected))

