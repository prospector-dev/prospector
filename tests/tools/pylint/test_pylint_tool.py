import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.pylint import PylintTool


def _get_pylint_tool_and_prospector_config(argv_patch=None):
    if argv_patch is None:
        argv_patch = [""]
    with patch("sys.argv", argv_patch):
        config = ProspectorConfig()
    pylint_tool = PylintTool()
    return pylint_tool, config


def _get_test_files(*names: str, workdir: Path = None):
    paths = [Path(__file__).parent / name for name in names]
    return FileFinder(*paths, workdir=workdir)


class TestPylintTool(TestCase):
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

    def test_use_pylint_default_path_finder(self):
        workdir = os.path.realpath("tests/tools/pylint/testpath/absolute-import/")
        pylint_tool, config = _get_pylint_tool_and_prospector_config(
            argv_patch=["", "-P", os.path.join(workdir, ".prospector", "pylint-default-finder.yml")]
        )
        found_files = _get_test_files("testpath/absolute-import/pkg", workdir=Path(workdir))
        pylint_tool.configure(config, found_files)
        pylint_tool.run(found_files)
