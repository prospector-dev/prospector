import re
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig


class TestProspectorConfig(TestCase):
    def test_determine_ignores_all_str(self):
        with patch("sys.argv", ["", "-P", "prospector-str-ignores"]), patch(
            "pathlib.Path.cwd", return_value=Path(__file__).parent
        ):
            config = ProspectorConfig()
        self.assertNotEqual(len(config.ignores), 0)
        boundary = r"(^|/|\\)%s(/|\\|$)"
        paths = ["2017", "2018"]
        for path in paths:
            compiled_ignored_path = re.compile(boundary % re.escape(path))
            self.assertIn(compiled_ignored_path, config.ignores)

    def test_determine_ignores_containing_int_values_wont_throw_attr_exc(self):
        try:
            with patch("sys.argv", ["", "-P", "prospector-int-ignores"]), patch(
                "pathlib.Path.cwd", return_value=Path(__file__).parent
            ):
                config = ProspectorConfig()
            self.assertNotEqual(len(config.ignores), 0)
            boundary = r"(^|/|\\)%s(/|\\|$)"
            paths = ["2017", "2018"]
            for path in paths:
                compiled_ignored_path = re.compile(boundary % re.escape(path))
                self.assertIn(compiled_ignored_path, config.ignores)
        except AttributeError as attr_exc:
            self.fail(attr_exc)
