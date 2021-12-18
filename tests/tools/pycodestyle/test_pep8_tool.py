import os
from unittest import TestCase
from unittest.mock import patch

from prospector._finder import find_python
from prospector.config import ProspectorConfig
from prospector.tools.pycodestyle import PycodestyleTool


class TestPycodestyleTool(TestCase):
    def setUp(self):
        with patch("sys.argv", [""]):
            self.config = ProspectorConfig()
        self._tool = PycodestyleTool()

    def test_absolute_path_is_computed_correctly(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        found_files = find_python([], [root], explicit_file_mode=True)
        self._tool.configure(self.config, found_files)
        self.assertNotEqual(self._tool.checker.paths, [os.path.join(*root_sep_split)])
        self.assertEqual(self._tool.checker.paths, [os.path.join(*root_os_split)])

    def test_pycodestyle_space_and_tabs(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "test_space_tab.py")
        found_files = find_python([], [root], explicit_file_mode=True)
        self._tool.configure(self.config, found_files)
        messages = self._tool.run([])
        self.assertTrue(any(message.code == "E101" for message in messages))
        self.assertTrue(any(message.code == "E111" for message in messages))
        self.assertTrue(any(message.code == "W191" for message in messages))
        self.assertTrue(all(message.source == "pycodestyle" for message in messages))

    # TODO: legacy config handling here:
    def test_find_pep8_section_in_config(self):
        workdir = os.path.join(os.path.dirname(__file__), "testsettings", "pep8")
        root = os.path.join(os.path.dirname(__file__), "testsettings", "pep8", "testfile.py")
        found_files = find_python([], [root], explicit_file_mode=True, workdir=workdir)
        configured_by, _ = self._tool.configure(self.config, found_files)
        expected_config_path = os.path.join(workdir, "setup.cfg")
        self.assertEqual(configured_by, "Configuration found at %s" % expected_config_path)

    def test_find_pycodestyle_section_in_config(self):
        workdir = os.path.join(os.path.dirname(__file__), "testsettings", "pycodestyle")
        root = os.path.join(os.path.dirname(__file__), "testsettings", "pycodestyle", "testfile.py")
        found_files = find_python([], [root], explicit_file_mode=True, workdir=workdir)
        configured_by, _ = self._tool.configure(self.config, found_files)
        expected_config_path = os.path.join(workdir, "setup.cfg")
        self.assertEqual(configured_by, "Configuration found at %s" % expected_config_path)
