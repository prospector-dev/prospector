"""
Tests that prospector raises the expected errors on the expected files depending on the
configuration of the file finder
"""
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools import PylintTool

from .utils import TEST_DATA


def test_total_errors():
    # There are 5 python files, all with the same error
    # Some are in sub-packages, one in a directory without an __init__
    # All should be found and exactly 1 error per file found
    workdir = TEST_DATA / "test_errors_found"
    with patch("sys.argv", ["prospector", str(workdir.absolute())]):
        config = ProspectorConfig()

    found_files = FileFinder(*config.paths)
    tool = PylintTool()
    tool.configure(config, found_files)
    messages = tool.run(found_files)

    assert len(messages) == 5

    message_locs = {m.location.path: m for m in messages}
    for file in workdir.rglob("*.py"):
        del message_locs[file]
    assert len(message_locs) == 0
