"""
Tests that prospector raises the expected errors on the expected files depending on the
configuration of the file finder
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.run import Prospector
from prospector.tools import PylintTool

from ..utils import patch_cli, patch_cwd, patch_execution

TEST_DATA = Path(__file__).parent / "testdata"


def test_non_subpath():
    """
    Create a temporary directory faaar away from the CWD when running, ensure prospector can run
    """
    tempdir = Path(tempfile.mkdtemp())
    try:
        with patch_execution(str(tempdir.absolute()), set_cwd=TEST_DATA / "something"):
            config = ProspectorConfig()
            pros = Prospector(config)
            pros.execute()
    finally:
        shutil.rmtree(tempdir)


def test_ignored():
    workdir = TEST_DATA / "ignore_test"
    with patch_execution("--profile", "profile.yml", str(workdir), set_cwd=workdir):
        config = ProspectorConfig()
        pros = Prospector(config)
        pros.execute()
        msgs = pros.get_messages()
        # only the pkg3.broken should be picked up as everything else is ignored
        assert len(msgs) == 1
        assert msgs[0].location.module == "pkg1.pkg2.pkg3.broken"


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
    # oddness here : Path.cwd() uses os.getcwd() under the hood in python<=3.9 but
    # for python 3.10+, they return different things if only one is patched; therefore,
    # for this test to work in all python versions prospector supports, both need to
    # be patched (or, an "if python version" statement but it's easier to just patch both)
    with patch_cwd(root):
        with patch_cli("prospector"):
            config1 = ProspectorConfig()
            found_files1 = FileFinder(*config1.paths)

        with patch_cli("prospector", "../relative_specified"):
            config2 = ProspectorConfig()
            found_files2 = FileFinder(*config1.paths)

        with patch_cli("prospector", "."):
            config3 = ProspectorConfig()
            found_files3 = FileFinder(*config1.paths)

    assert root == config2.workdir == config1.workdir == config3.workdir
    assert config1.paths == config2.paths == config3.paths

    assert found_files3.files == found_files2.files == found_files1.files
    assert found_files3.python_modules == found_files2.python_modules == found_files1.python_modules
    assert found_files3.python_packages == found_files2.python_packages == found_files1.python_packages
    assert found_files3.directories == found_files2.directories == found_files1.directories
