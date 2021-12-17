import os
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import find_python
from prospector.tools.pylint import PylintTool


def _get_pylint_tool_and_prospector_config(argv_patch=None):
    if argv_patch is None:
        argv_patch = [""]
    with patch("sys.argv", argv_patch):
        config = ProspectorConfig()
    pylint_tool = PylintTool()
    return pylint_tool, config


class TestPylintTool(TestCase):
    def test_absolute_path_is_computed_correctly(self):
        pylint_tool, config = _get_pylint_tool_and_prospector_config()
        root = os.path.join(os.path.dirname(__file__), "testpath", "test.py")
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        found_files = find_python([], [root], explicit_file_mode=True)
        pylint_tool.configure(config, found_files)
        self.assertNotEqual(pylint_tool._args, [os.path.join(*root_sep_split)])
        self.assertEqual(pylint_tool._args, [os.path.join(*root_os_split)])

    def test_wont_throw_false_positive_relative_beyond_top_level(self):
        with patch("os.getcwd", return_value=os.path.realpath("tests/tools/pylint/testpath/")):
            pylint_tool, config = _get_pylint_tool_and_prospector_config()
        root = os.path.join(os.path.dirname(__file__), "testpath", "src", "mcve", "foobar.py")
        found_files = find_python([], [root], explicit_file_mode=True)
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        self.assertListEqual(messages, [])

    def test_will_throw_useless_suppression(self):
        with patch("os.getcwd", return_value=os.path.realpath("tests/tools/pylint/testpath/")):
            pylint_tool, config = _get_pylint_tool_and_prospector_config(argv_patch=["", "-t", "pylint"])
        root = os.path.join(os.path.dirname(__file__), "testpath", "test_useless_suppression.py")
        found_files = find_python([], [root], explicit_file_mode=True)
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        assert any(
            m.code == "useless-suppression" for m in messages
        ), "There should be at least one useless suppression"

    def test_use_pylint_default_path_finder(self):
        workdir = os.path.realpath("tests/tools/pylint/testpath/absolute-import/")
        pylint_tool, config = _get_pylint_tool_and_prospector_config(
            argv_patch=["", "-P", os.path.join(workdir, ".prospector", "pylint-default-finder.yml")]
        )
        root = os.path.join(os.path.dirname(__file__), "testpath", "absolute-import", "pkg")
        found_files = find_python([], [root], False, workdir)
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        self.assertListEqual(messages, [])

    def test_use_prospector_default_path_finder(self):
        workdir = "tests/tools/pylint/testpath/absolute-import/"
        with patch("os.getcwd", return_value=os.path.realpath(workdir)):
            pylint_tool, config = _get_pylint_tool_and_prospector_config(
                argv_patch=["", "-P", "prospector-default-finder"]
            )
        root = os.path.join(os.path.dirname(__file__), "testpath", "absolute-import", "pkg")
        found_files = find_python([], [root], False)
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        self.assertEqual(messages[0].code, "no-name-in-module")
