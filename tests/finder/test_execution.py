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


def test_relative_path_specified():
    """
    This test was to fix `prospector .` returning different results to `prospector ../prospector`
    (when running inside the prospector checkout
    """
    root = TEST_DATA / "relative_specified"
    with patch("os.getcwd", new=lambda: str(root.absolute())):
        with patch("sys.argv", ["prospector"]):
            config1 = ProspectorConfig()
            found_files1 = FileFinder(*config1.paths)

        with patch("sys.argv", ["prospector", "../relative_specified"]):
            config2 = ProspectorConfig()
            found_files2 = FileFinder(*config1.paths)

        with patch("sys.argv", ["prospector", "."]):
            config3 = ProspectorConfig()
            found_files3 = FileFinder(*config1.paths)

    assert root == config2.workdir == config1.workdir == config3.workdir
    assert config1.paths == config2.paths == config3.paths

    assert found_files3.files == found_files2.files == found_files1.files
    assert found_files3.python_modules == found_files2.python_modules == found_files1.python_modules
    assert found_files3.python_packages == found_files2.python_packages == found_files1.python_packages
    assert found_files3.directories == found_files2.directories == found_files1.directories
