from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.vulture import VultureTool


class TestVultureTool(TestCase):
    def setUp(self):
        with patch("sys.argv", [""]):
            self.config = ProspectorConfig()
        self.vulture_tool = VultureTool()

    def test_vulture_find_dead_code(self):
        found_files = FileFinder(Path(__file__).parent / "testpath/testfile.py")
        self.vulture_tool.configure(self.config, found_files)
        messages = self.vulture_tool.run(found_files)
        self.assertTrue(any(message.code in ["unused-variable", "unused-import"] for message in messages))
