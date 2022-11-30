import re
from pathlib import Path

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder

from ..utils import patch_execution


def test_relative_ignores():
    """
    Tests that if 'ignore-paths: something' is set, then it is ignored; that
    is, paths relative to the working directory should be ignored too
    """
    workdir = Path(__file__).parent / "testdata/test_relative_ignores"
    with patch_execution("-P", "profile_relative_ignores.yml", set_cwd=workdir):
        config = ProspectorConfig()
        files = FileFinder(*config.paths, exclusion_filters=[config.make_exclusion_filter()])
        assert 2 == len(files.python_modules)


def test_determine_ignores_all_str():
    with patch_execution("-P", "prospector-str-ignores", set_cwd=Path(__file__).parent):
        config = ProspectorConfig()
    assert len(config.ignores) > 0
    boundary = r"(^|/|\\)%s(/|\\|$)"
    paths = ["2017", "2018"]
    for path in paths:
        compiled_ignored_path = re.compile(boundary % re.escape(path))
        assert compiled_ignored_path in config.ignores


def test_determine_ignores_containing_int_values_wont_throw_attr_exc():
    with patch_execution("-P", "prospector-int-ignores", set_cwd=Path(__file__).parent):
        config = ProspectorConfig()
    assert len(config.ignores) > 0
    boundary = r"(^|/|\\)%s(/|\\|$)"
    paths = ["2017", "2018"]
    for path in paths:
        compiled_ignored_path = re.compile(boundary % re.escape(path))
        assert compiled_ignored_path in config.ignores
