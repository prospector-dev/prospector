import os
from pathlib import Path
from typing import Tuple
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.pylint import PylintTool

THIS_DIR = Path(__file__).parent


def _get_pylint_tool_and_prospector_config(argv_patch=None) -> Tuple[PylintTool, ProspectorConfig]:
    if argv_patch is None:
        argv_patch = [""]
    with patch("sys.argv", argv_patch):
        config = ProspectorConfig()
    pylint_tool = PylintTool()
    return pylint_tool, config


def _get_test_files(*names: str, exclusion_filters=None):
    paths = [THIS_DIR / name for name in names]
    return FileFinder(*paths, exclusion_filters=exclusion_filters)


class TestPylintTool(TestCase):
    def test_checkpath_includes_no_init_modules(self):
        """
        If a subdirectory of a package has a .py file but no __init__.py it should still be included
        """
        files = _get_test_files("test_no_init_found")
        tool, config = _get_pylint_tool_and_prospector_config()
        check_paths = tool._get_pylint_check_paths(files)
        assert len(check_paths) == 2
        assert sorted(Path(p).name for p in check_paths) == ["file3.py", "test_no_init_found"]

    def test_no_duplicates_in_checkpath(self):
        """
        This checks that the pylint tool will not generate a list of packages and subpackages -
        if there is a hierarchy there is no need to duplicate sub-packages in the list to be checked
        """
        root = THIS_DIR / "duplicates_test"
        files = FileFinder(root)
        tool, config = _get_pylint_tool_and_prospector_config()
        check_paths = tool._get_pylint_check_paths(files)
        assert len(check_paths) == 1
        assert [str(Path(p).relative_to(root)) for p in check_paths] == ["pkg1"]

    def test_pylint_config(self):
        """Verifies that prospector will configure pylint with any pylint-specific configuration if found"""

        def _has_message(msg_list, code):
            return any([message.code == code and message.source == "pylint" for message in msg_list])

        for config_type in ("pylintrc", "pylintrc2", "pyproject", "setup.cfg"):
            root = THIS_DIR / "pylint_configs" / config_type

            with patch("pathlib.Path.cwd", return_value=root.absolute()):
                pylint_tool, config = _get_pylint_tool_and_prospector_config()
            self.assertEqual(Path(config.workdir).absolute(), root.absolute())

            found_files = _get_test_files(root)
            pylint_tool.configure(config, found_files)

            messages = pylint_tool.run(found_files)
            self.assertTrue(_has_message(messages, "line-too-long"), msg=config_type)

    def test_absolute_path_is_computed_correctly(self):
        pylint_tool, config = _get_pylint_tool_and_prospector_config()
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        found_files = _get_test_files("testpath/testfile.py")
        pylint_tool.configure(config, found_files)
        self.assertNotEqual(pylint_tool._args, [os.path.join(*root_sep_split)])
        self.assertEqual(pylint_tool._args, [os.path.join(*root_os_split)])

    def test_wont_throw_false_positive_relative_beyond_top_level(self):
        with patch("os.getcwd", return_value=os.path.realpath("tests/tools/pylint/testpath/")):
            pylint_tool, config = _get_pylint_tool_and_prospector_config()
        found_files = _get_test_files("testpath/src/mcve/foobar.py")
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        self.assertListEqual(messages, [])

    def test_will_throw_useless_suppression(self):
        with patch("os.getcwd", return_value=os.path.realpath("tests/tools/pylint/testpath/")):
            pylint_tool, config = _get_pylint_tool_and_prospector_config(argv_patch=["", "-t", "pylint"])

        found_files = _get_test_files("testpath", "testpath/test_useless_suppression.py")
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        assert any(
            m.code == "useless-suppression" for m in messages
        ), "There should be at least one useless suppression"

    def test_parallel_execution(self):
        root = THIS_DIR / "parallel"

        with patch("pathlib.Path.cwd", return_value=root.absolute()):
            pylint_tool, config = _get_pylint_tool_and_prospector_config()
        self.assertEqual(Path(config.workdir).absolute(), root.absolute())

        found_files = _get_test_files(root, exclusion_filters=[config.make_exclusion_filter()])
        pylint_tool.configure(config, found_files)
        assert pylint_tool._linter.config.jobs == 2

        messages = pylint_tool.run(found_files)
        assert "line-too-long" in [msg.code for msg in messages if msg.source == "pylint"]
