import os
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import find_python
from prospector.tools.bandit import BanditTool


class TestBanditTool(TestCase):
    def setUp(self):
        with patch("sys.argv", [""]):
            self.config = ProspectorConfig()
        self.bandit_tool = BanditTool()

    def test_hardcoded_password_string(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        found_files = find_python([], [root], explicit_file_mode=True)
        self.bandit_tool.configure(self.config, found_files)
        messages = self.bandit_tool.run(found_files)
        self.assertTrue(any(message.code in ["B107", "B105", "B106"] for message in messages))
