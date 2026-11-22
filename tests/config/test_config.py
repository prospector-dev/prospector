import re
from pathlib import Path

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder

from ..utils import patch_execution


def test_relative_ignores() -> None:
    """
    Tests that if 'ignore-paths: something' is set, then it is ignored; that
    is, paths relative to the working directory should be ignored too
    """
    workdir = Path(__file__).parent / "testdata/test_relative_ignores"
    with patch_execution("-P", "profile_relative_ignores.yml", set_cwd=workdir):
        config = ProspectorConfig()
        files = FileFinder(*config.paths, exclusion_filters=[config.make_exclusion_filter()])
        assert len(files.python_modules) == 2


def test_symlinked_ignore_path(tmp_path: Path) -> None:
    """
    Tests that 'ignore-paths: <symlink name>' ignores the symlink itself,
    not only the path its target resolves to.
    """
    target = tmp_path / "realdir"
    target.mkdir()
    (target / "module.py").write_text("x = 1\n")
    (tmp_path / "link").symlink_to(target, target_is_directory=True)
    (tmp_path / "profile_symlink_ignores.yml").write_text("ignore-paths:\n  - link\n")

    with patch_execution("-P", "profile_symlink_ignores.yml", set_cwd=tmp_path):
        config = ProspectorConfig()
        exclusion_filter = config.make_exclusion_filter()

    assert exclusion_filter(tmp_path / "link")
    assert exclusion_filter(tmp_path / "link" / "module.py")


def test_determine_ignores_all_str() -> None:
    with patch_execution("-P", "prospector-str-ignores", set_cwd=Path(__file__).parent):
        config = ProspectorConfig()
    assert len(config.ignores) > 0
    boundary = r"(^|/|\\)%s(/|\\|$)"
    paths = ["2017", "2018"]
    for path in paths:
        compiled_ignored_path = re.compile(boundary % re.escape(path))
        assert compiled_ignored_path in config.ignores


def test_determine_ignores_containing_int_values_wont_throw_attr_exc() -> None:
    with patch_execution("-P", "prospector-int-ignores", set_cwd=Path(__file__).parent):
        config = ProspectorConfig()
    assert len(config.ignores) > 0
    boundary = r"(^|/|\\)%s(/|\\|$)"
    paths = ["2017", "2018"]
    for path in paths:
        compiled_ignored_path = re.compile(boundary % re.escape(path))
        assert compiled_ignored_path in config.ignores


def test_pyproject_profile_autoloaded(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[tool.prospector]\nignore-paths = ["build"]\n')

    with patch_execution(set_cwd=tmp_path):
        config = ProspectorConfig()

    assert config.profile.name == "pyproject.toml"
    assert config.profile.ignore_paths == ["build"]
    assert config.strictness == "from profile"


def test_pyproject_without_tool_prospector_ignored(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.black]\nline-length = 100\n")

    with patch_execution(set_cwd=tmp_path):
        config = ProspectorConfig()

    assert config.profile.name == "default"


def test_prospector_yaml_takes_precedence_over_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[tool.prospector]\nignore-paths = ["build"]\n')
    (tmp_path / ".prospector.yaml").write_text("ignore-paths:\n  - docs\n")

    with patch_execution(set_cwd=tmp_path):
        config = ProspectorConfig()

    assert config.profile.name == ".prospector.yaml"
    assert config.profile.ignore_paths == ["docs"]


def test_explicit_profile_overrides_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[tool.prospector]\nignore-paths = ["build"]\n')

    with patch_execution("--profile", "strictness_high", set_cwd=tmp_path):
        config = ProspectorConfig()

    assert config.profile.name == "strictness_high"
    assert "build" not in config.profile.ignore_paths
