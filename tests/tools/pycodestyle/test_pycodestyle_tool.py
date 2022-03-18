import os
from pathlib import Path
from unittest import TestCase

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.pycodestyle import PycodestyleTool

from ...utils import patch_cli, patch_cwd, patch_execution


class TestPycodestyleTool(TestCase):
    def setUp(self):
        self._tool = PycodestyleTool()

    def _configure(self, filename, *cli_args, workdir=None):
        with patch_execution(*cli_args, set_cwd=workdir):
            found_files = FileFinder(Path(__file__).parent / filename)
            config = ProspectorConfig(workdir)
            return self._tool.configure(config, found_files)

    def test_absolute_path_is_computed_correctly(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        self._configure("testpath/testfile.py")
        self.assertNotEqual(self._tool.checker.paths, [os.path.join(*root_sep_split)])
        self.assertEqual(self._tool.checker.paths, [os.path.join(*root_os_split)])

    def test_pycodestyle_space_and_tabs(self):
        workdir = Path(__file__).parent / "testpath"
        self._configure("testpath/test_space_tab.py", "--full-pep8", workdir=workdir)
        messages = self._tool.run([])
        self.assertTrue(all(message.source == "pycodestyle" for message in messages))
        self.assertTrue({"E101", "E111", "W191"} <= {m.code for m in messages})

    # TODO: legacy config handling here:
    def test_find_pep8_section_in_config(self):
        workdir = Path(__file__).parent / "testsettings/pep8"
        configured_by, _ = self._configure("testsettings/pep8/testfile.py", workdir=workdir)
        expected_config_path = str(workdir / "setup.cfg")
        self.assertEqual(configured_by, "Configuration found at %s" % expected_config_path)

    def test_find_pycodestyle_section_in_config(self):
        workdir = Path(__file__).parent / "testsettings/pycodestyle"
        configured_by, _ = self._configure("testsettings/pycodestyle/testfile.py", workdir=workdir)
        expected_config_path = str(workdir / "setup.cfg")
        self.assertEqual(configured_by, "Configuration found at %s" % expected_config_path)
