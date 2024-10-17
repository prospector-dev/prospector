from unittest import TestCase
from unittest.mock import patch

from prospector.config.datatype import parse_output_format


class TestOutputChoice(TestCase):
    @patch("sys.platform", "linux")
    @patch("os.path.sep", "/")
    @patch("os.path.altsep", None)
    def test_sanitize_rel_path_colon_posix(self):
        self.assertEqual(
            parse_output_format("pylint:./test-results.xml"),
            ("pylint", ["./test-results.xml"]),
        )

    @patch("sys.platform", "linux")
    @patch("os.path.sep", "/")
    @patch("os.path.altsep", None)
    def test_sanitize_rel_path_semicolon_posix(self):
        self.assertEqual(
            parse_output_format("pylint;./test-results.xml"),
            ("pylint", ["./test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_rel_path_colon_windows(self):
        self.assertEqual(
            parse_output_format("pylint:.\\test-results.xml"),
            ("pylint", [".\\test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_rel_path_semicolon_windows(self):
        self.assertEqual(
            parse_output_format("pylint;.\\test-results.xml"),
            ("pylint", [".\\test-results.xml"]),
        )

    @patch("sys.platform", "linux")
    @patch("os.path.sep", "/")
    @patch("os.path.altsep", None)
    def test_sanitize_abs_path_colon_posix(self):
        self.assertEqual(
            parse_output_format("pylint:/home/test-results.xml"),
            ("pylint", ["/home/test-results.xml"]),
        )

    @patch("sys.platform", "linux")
    @patch("os.path.sep", "/")
    @patch("os.path.altsep", None)
    def test_sanitize_abs_path_semicolon_posix(self):
        self.assertEqual(
            parse_output_format("pylint;/home/test-results.xml"),
            ("pylint", ["/home/test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_abs_path_colon_windows(self):
        self.assertEqual(
            parse_output_format("pylint:C:\\testResults\\test-results.xml"),
            ("pylint", ["C:\\testResults\\test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_abs_path_semicolon_windows(self):
        self.assertEqual(
            parse_output_format("pylint;C:\\testResults\\test-results.xml"),
            ("pylint", ["C:\\testResults\\test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_abs_path_colon_windows_alternate(self):
        self.assertEqual(
            parse_output_format("pylint:C:/testResults/test-results.xml"),
            ("pylint", ["C:/testResults/test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_abs_path_semicolon_windows_alternate(self):
        self.assertEqual(
            parse_output_format("pylint;C:/testResults/test-results.xml"),
            ("pylint", ["C:/testResults/test-results.xml"]),
        )

    @patch("sys.platform", "linux")
    @patch("os.path.sep", "/")
    @patch("os.path.altsep", None)
    def test_sanitize_abs_rel_path_colon_posix(self):
        self.assertEqual(
            parse_output_format("pylint:/home/test-results.xml:./test-results.xml"),
            ("pylint", ["/home/test-results.xml", "./test-results.xml"]),
        )

    @patch("sys.platform", "linux")
    @patch("os.path.sep", "/")
    @patch("os.path.altsep", None)
    def test_sanitize_abs_rel_path_semicolon_posix(self):
        self.assertEqual(
            parse_output_format("pylint;/home/test-results.xml;./test-results.xml"),
            ("pylint", ["/home/test-results.xml", "./test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_abs_rel_path_colon_windows(self):
        self.assertEqual(
            parse_output_format("pylint:C:\\home\\test-results.xml:.\\test-results.xml"),
            ("pylint", ["C:\\home\\test-results.xml", ".\\test-results.xml"]),
        )

    @patch("sys.platform", "win32")
    @patch("os.path.sep", "\\")
    @patch("os.path.altsep", "/")
    def test_sanitize_abs_rel_path_semicolon_windows(self):
        self.assertEqual(
            parse_output_format("pylint;C:\\home\\test-results.xml;.\\test-results.xml"),
            ("pylint", ["C:\\home\\test-results.xml", ".\\test-results.xml"]),
        )
