import os
import tempfile
import re
from unittest import TestCase
from prospector.finder import find_python
from prospector.tools.pep8 import Pep8Tool
from prospector.config import ProspectorConfig


# A very basic stub to avoid creating a real ProspectorConfig, which isn't
# esasily tweakable for tests "from the outside".
# Needed for handing into the Pep8Tool.configure(...) method, should expose at
# least the ProspectorConfig interface accessed by this method.
class StubProspectorConfig(object):

    def __init__(self, external_config=None, ignores=None,
                 max_line_length=300):
        # external_config: optional file path to pep8/pycodestyle config file
        # ignores: list of regular expressions strings of (relative) paths to
        #     ignore
        # max_line_length: value for the max_line_length property, not
        #     currently actually used for anything here, default to s.th.
        #     "big"
        self.external_config = external_config
        if ignores is None:
            self.ignores = [] 
        else:
            self.ignores = [re.compile(patt) for patt in ignores]
        self._max_line_length = max_line_length

    # stubbed ProspectorConfig API
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


def dummy_checker():
    # create a fake checker that gathers the filenames into
    # DummyChecker.filenames class attribute
    class DummyChecker(object):
        filenames = []

        def __init__(self, filename, *args, **kwargs):
            self.filenames.append(filename)

        def check_all(self, *args, **kwargs):
            pass

    return DummyChecker


# helper function
def prepend_root(paths, root=None):
    """Return list of paths with root dir prepended to each path."""
    if root:
        return [os.path.normpath(os.path.join(root, p)) for p in paths]
    return paths


class TestProspectorStyleGuidePathConfig(TestCase):
    # Test how prospector sets up the pep8/pycodestyle tool with regard to the
    # paths to check.
    # We need to create the ProspectorStyleGuide through a Pep8Tool instance
    # and use finder.find_python to create the input for Pep8Tool.configure()

    def _setup_styleguide(self, paths, ignores=None, external_config=None):
        # A helper to create the StyleGuide object.
        # root: the root directory for the relative paths given in the paths
        #     and expected parameters
        pep8tool = Pep8Tool()
        config = StubProspectorConfig(
            external_config=external_config, ignores=ignores)
        found_python = find_python(
            ignores=config.ignores, paths=paths,
            explicit_file_mode=True if len(paths)>1 else False)

        configured_by, _ = pep8tool.configure(config, found_python)
        if external_config is not None:
            expected_configuration_message = (
                "Configuration found at %s" % external_config)
            self.assertEqual(configured_by, expected_configuration_message) 
        prospector_styleguide = pep8tool.checker
        # inject file paths-gathering dummy checker and invoke it
        prospector_styleguide.checker_class = dummy_checker()
        prospector_styleguide.check_files()
        return prospector_styleguide

    def test_paths_dir_arg(self):
        # test corresponding to a single command line PATH dir arg
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        # use the root directory itself as find_python input arg:
        paths = prepend_root([''], root)
        # all Python modules in the directory tree are expected (but nothing 
        # else)
        expected = prepend_root(
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module1.py',
             'package/subpackage/subpackage_module2.py',
             'package/package_module1.py',
             'package/package_module2.py',
             'nonpackage/nonpackage_module1.py',
             'nonpackage/nonpackage_module2.py',
             'module1.py',
             'module2.py',
             ], root)

        prospector_styleguide = self._setup_styleguide(paths)
        self.assertEqual(
            sorted(prospector_styleguide.checker_class.filenames),
            sorted(expected))

    def test_paths_dir_arg_prospector_ignore_patterns_cfg(self):
        # test corresponding to a single command line PATH dir arg, with
        # with prospectorer ignore-patterns 
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        # use the root directory itself as find_python input arg:
        paths = prepend_root([''], root)

        ignores = ['(^|/)subpackage(/|$)', 'nonpackage', '^package/module1.py$']
        expected = prepend_root(
            ['package/__init__.py',
             #'package/subpackage/__init__.py',
             #'package/subpackage/subpackage_module1.py',
             #'package/subpackage/subpackage_module2.py',
             #'package/package_module1.py',
             'package/package_module2.py',
             #'nonpackage/nonpackage_module1.py',
             #'nonpackage/nonpackage_module2.py',
             'module1.py',
             'module2.py',
             ], root)
        prospector_styleguide = self._setup_styleguide(paths, ignores=ignores)
        self.assertEqual(
            sorted(prospector_styleguide.checker_class.filenames),
            sorted(expected))

    def test_paths_dir_arg_pep8_exclude_cfg(self):
        # test corresponding to a single command line PATH dir arg, with
        # external pep8/pycodestyle config file to exclude the 'subpackage'
        # folder from checking
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        # use the root directory itself as find_python input arg:
        paths = prepend_root([''], root)

        # set pep8/pycodestyle exclude config option
        external_config_contents = """
[pep8]
exclude = subpackage
        """
        expected = prepend_root(
            ['package/__init__.py',
             #'package/subpackage/__init__.py',
             #'package/subpackage/subpackage_module1.py',
             #'package/subpackage/subpackage_module2.py',
             'package/package_module1.py',
             'package/package_module2.py',
             'nonpackage/nonpackage_module1.py',
             'nonpackage/nonpackage_module2.py',
             'module1.py',
             'module2.py',
             ], root)
        with tempfile.NamedTemporaryFile() as f:
            f.write(external_config_contents)
            f.flush()
            prospector_styleguide = self._setup_styleguide(
                paths, external_config=f.name)
            self.assertEqual(
                sorted(prospector_styleguide.checker_class.filenames),
                sorted(expected))

    def test_paths_py_modules_arg(self):
        # test corresponding to multiple Python module files PATHs args
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        paths = prepend_root(
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module1.py',
             'package/subpackage/subpackage_module2.py',
             'package/package_module1.py',
             'package/package_module2.py',
             'nonpackage/nonpackage_module1.py',
             'nonpackage/nonpackage_module2.py',
             'module1.py',
             'module2.py',
             ], root)

        # all Python modules given as paths args are expected (but nothing 
        # else)
        expected = prepend_root(
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_module1.py',
             'package/subpackage/subpackage_module2.py',
             'package/package_module1.py',
             'package/package_module2.py',
             'nonpackage/nonpackage_module1.py',
             'nonpackage/nonpackage_module2.py',
             'module1.py',
             'module2.py',
             ], root)
        prospector_styleguide = self._setup_styleguide(paths)
        self.assertEqual(
            sorted(prospector_styleguide.checker_class.filenames),
            sorted(expected))

    def test_paths_files_arg(self):
        # test corresponding to multiple files PATHs args (Python modules and
        # other files)
        root = os.path.join(
            os.path.dirname(__file__), '..', 'finder', 'testdata',
            'dirs_mods_packages')
        paths = prepend_root(
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_plain.txt',
             'package/subpackage/subpackage_module1.py',
             'package/subpackage/subpackage_module2.py',
             'package/package_module1.py',
             'package/package_module2.py',
             'package/package_plain.txt',
             'nonpackage/nonpackage_module1.py',
             'nonpackage/nonpackage_module2.py',
             'nonpackage/nonpackage_plain.txt',
             'module1.py',
             'module2.py',
             'plain.txt',
             ], root)

        # all files given as path args are expected (but nothing 
        # else)
        # TODO: Is this how it should work? Should the tools cater for
        # TODO: filtering non-Python files?
        expected = prepend_root(
            ['package/__init__.py',
             'package/subpackage/__init__.py',
             'package/subpackage/subpackage_plain.txt',
             'package/subpackage/subpackage_module1.py',
             'package/subpackage/subpackage_module2.py',
             'package/package_module1.py',
             'package/package_module2.py',
             'package/package_plain.txt',
             'nonpackage/nonpackage_module1.py',
             'nonpackage/nonpackage_module2.py',
             'nonpackage/nonpackage_plain.txt',
             'module1.py',
             'module2.py',
             'plain.txt',
             ], root)

        prospector_styleguide = self._setup_styleguide(paths)
        self.assertEqual(
            sorted(prospector_styleguide.checker_class.filenames),
            sorted(expected))

