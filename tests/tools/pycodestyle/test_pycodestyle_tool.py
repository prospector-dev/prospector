import os
from pathlib import Path
from unittest import TestCase

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.pycodestyle import PycodestyleTool


def _get_test_files(name):
    return FileFinder(Path(__file__).parent / name)


class TestPycodestyleTool(TestCase):
    def setUp(self):
        self._tool = PycodestyleTool()

    def test_absolute_path_is_computed_correctly(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        found_files = _get_test_files("testpath/testfile.py")
        self._tool.configure(ProspectorConfig(), found_files)
        self.assertNotEqual(self._tool.checker.paths, [os.path.join(*root_sep_split)])
        self.assertEqual(self._tool.checker.paths, [os.path.join(*root_os_split)])

    def test_pycodestyle_space_and_tabs(self):
        found_files = _get_test_files("testpath/test_space_tab.py")
        self._tool.configure(ProspectorConfig(), found_files)
        messages = self._tool.run([])
        self.assertTrue(any(message.code == "E101" for message in messages))
        self.assertTrue(any(message.code == "E111" for message in messages))
        self.assertTrue(any(message.code == "W191" for message in messages))
        self.assertTrue(all(message.source == "pycodestyle" for message in messages))

    # TODO: legacy config handling here:
    def test_find_pep8_section_in_config(self):
        workdir = Path(__file__).parent / "testsettings/pep8"
        config = ProspectorConfig(workdir)
        found_files = _get_test_files("testsettings/pep8/testfile.py")
        configured_by, _ = self._tool.configure(config, found_files)
        expected_config_path = str(workdir / "setup.cfg")
        self.assertEqual(configured_by, "Configuration found at %s" % expected_config_path)

    def test_find_pycodestyle_section_in_config(self):
        workdir = Path(__file__).parent / "testsettings/pycodestyle"
        config = ProspectorConfig(workdir)
        found_files = _get_test_files("testsettings/pycodestyle/testfile.py")
        configured_by, _ = self._tool.configure(config, found_files)
        expected_config_path = str(workdir / "setup.cfg")
        self.assertEqual(configured_by, "Configuration found at %s" % expected_config_path)
