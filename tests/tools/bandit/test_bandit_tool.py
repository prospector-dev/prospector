# -*- coding: utf-8 -*-
import os
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import find_python
from prospector.tools.bandit import BanditTool


class TestBanditTool(TestCase):
    def setUp(self):
        with patch("sys.argv", ["'"]):
            self.config = ProspectorConfig()
        self.bandit_tool = BanditTool()

    def test_hardcoded_password_string(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        found_files = find_python([], [root], explicit_file_mode=True)
        self.bandit_tool.configure(self.config, found_files)
        messages = self.bandit_tool.run(found_files)
        expected_messages_list = [
            {"code": "B107", "line": 1},
            {"code": "B107", "line": 16},
            {"code": "B106", "line": 22},
        ]
        for index, message in enumerate(messages):
            with self.subTest(i=index):
                message_dict = {"code": message.code, "line": message.location.line}
                expected_message_dict = expected_messages_list[index]
                self.assertEqual(message_dict, expected_message_dict)
