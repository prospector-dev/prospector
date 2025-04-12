from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.bandit import BanditTool


class TestBanditTool(TestCase):
    def setUp(self) -> None:
        with patch("sys.argv", [""]):
            self.config = ProspectorConfig()
        self.bandit_tool = BanditTool()

    def test_hardcoded_password_string(self) -> None:
        found_files = FileFinder(Path(__file__).parent / "testpath/testfile.py")
        self.bandit_tool.configure(self.config, found_files)
        messages = self.bandit_tool.run(found_files)
        assert any(message.code in ["B107", "B105", "B106"] for message in messages)
