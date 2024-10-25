from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.ruff import RuffTool


class test_ruff_tool:
    with patch("sys.argv", []):
        config = ProspectorConfig()
    ruff_tool = RuffTool()

    found_files = FileFinder(Path(__file__).parent / "testpath/testfile.py")
    ruff_tool.configure(config, found_files)
    messages = ruff_tool.run(found_files)
    assert {"S105", "S106", "S107"} == {message.code for message in messages}
