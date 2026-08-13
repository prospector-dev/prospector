from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from vulture.config import DEFAULTS

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.vulture import ProspectorVulture, VultureTool


class TestVultureTool(TestCase):
    def setUp(self) -> None:
        with patch("sys.argv", [""]):
            self.config = ProspectorConfig()
        self.vulture_tool = VultureTool()

    def test_vulture_reads_pyproject_config(self) -> None:
        """
        `[tool.vulture]` in pyproject.toml is honoured.

        Vulture reads that section itself, so without this the same project
        gets different results from `vulture` and from `prospector`.

        see https://github.com/prospector-dev/prospector/issues/505
        """
        testpath = Path(__file__).parent / "pyproject_config"
        with patch("sys.argv", [""]):
            config = ProspectorConfig(workdir=testpath)

        found_files = FileFinder(testpath / "app.py")
        tool = VultureTool()
        tool.configure(config, found_files)
        messages = [message.message for message in tool.run(found_files)]

        # ignored by `ignore_decorators`, and by `ignore_names`
        for name in ("read_items", "create_item", "keep_me"):
            assert not any(name in message for message in messages), f"{name} should have been ignored, got {messages}"

        # everything else is still reported
        assert any("truly_unused" in message for message in messages), messages

    def test_vulture_honours_min_confidence(self) -> None:
        testfile = Path(__file__).parent / "pyproject_config" / "app.py"

        default_vulture = ProspectorVulture(FileFinder(testfile), DEFAULTS)
        default_vulture.scavenge()
        assert any("truly_unused" in message.message for message in default_vulture.get_messages())

        strict_config = {**DEFAULTS, "min_confidence": 100}
        strict_vulture = ProspectorVulture(FileFinder(testfile), strict_config)
        strict_vulture.scavenge()
        assert not any("truly_unused" in message.message for message in strict_vulture.get_messages())

    def test_vulture_find_dead_code(self) -> None:
        found_files = FileFinder(Path(__file__).parent / "testpath/testfile.py")
        self.vulture_tool.configure(self.config, found_files)
        messages = self.vulture_tool.run(found_files)
        assert any(message.code in ["unused-variable", "unused-import"] for message in messages)
