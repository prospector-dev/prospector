# -*- coding: utf-8 -*-
import os
import sys
from unittest import TestCase

from prospector.config import ProspectorConfig
from prospector.finder import find_python
from prospector.tools.pylint import PylintTool

if sys.version_info >= (3, 0):
    from unittest.mock import patch
else:
    from mock import patch


class TestPylintTool(TestCase):
    def setUp(self):
        with patch('sys.argv', ['']):
            self.config = ProspectorConfig()
        self.pylint_tool = PylintTool()

    def test_absolute_path_is_computed_correctly(self):
        root = os.path.join(os.path.dirname(__file__), 'testpath', 'test.py')
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        found_files = find_python([], [root], explicit_file_mode=True)
        self.pylint_tool.configure(self.config, found_files)
        self.assertNotEqual(self.pylint_tool._args,
                            [os.path.join(*root_sep_split)])
        self.assertEqual(self.pylint_tool._args,
                         [os.path.join(*root_os_split)])
