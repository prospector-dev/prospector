from pathlib import Path

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.vulture import VultureTool
from tests.utils import patch_execution

PYPROJECT = """[tool.vulture]
ignore_decorators = ["@app.route"]
"""

MODULE = """import app


@app.route
def handler():
    return 1
"""


def _run_vulture(workdir: Path, module: Path) -> list[str]:
    with patch_execution(set_cwd=workdir):
        config = ProspectorConfig()
    found_files = FileFinder(module)
    tool = VultureTool()
    tool.configure(config, found_files)
    return [message.message for message in tool.run(found_files)]


def test_vulture_uses_ignore_decorators_from_pyproject_toml(tmp_path: Path) -> None:
    """Vulture configuration in pyproject.toml must be honoured (issue #505)."""
    (tmp_path / "pyproject.toml").write_text(PYPROJECT)
    module = tmp_path / "code.py"
    module.write_text(MODULE)

    assert _run_vulture(tmp_path, module) == []


def test_vulture_still_reports_when_pyproject_toml_does_not_ignore_it(tmp_path: Path) -> None:
    """Control: without the configuration the same code is still reported."""
    (tmp_path / "pyproject.toml").write_text("[tool.other]\n")
    module = tmp_path / "code.py"
    module.write_text(MODULE)

    assert _run_vulture(tmp_path, module) == ["Unused function 'handler'"]
