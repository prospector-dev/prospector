# -*- coding: utf-8 -*-
import os
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import find_python
from prospector.tools.vulture import VultureTool


class TestVultureTool(TestCase):
    def setUp(self):
        with patch("sys.argv", [""]):
            self.config = ProspectorConfig()
        self.vulture_tool = VultureTool()

    def test_vulture_find_dead_code(self):
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        found_files = find_python([], [root], explicit_file_mode=True)
        self.vulture_tool.configure(self.config, found_files)
        messages = self.vulture_tool.run(found_files)
        self.assertTrue(any(message.code in ["unused-variable", "unused-import"] for message in messages))
