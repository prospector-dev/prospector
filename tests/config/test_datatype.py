from unittest import TestCase
from prospector.config.datatype import OutputChoice


class TestOutputChoice(TestCase):

    def test_sanitize_rel_path_colon_posix(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit:./test-results.xml'), ('xunit', ['./test-results.xml']))

    def test_sanitize_rel_path_semicolon_posix(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit;./test-results.xml'), ('xunit', ['./test-results.xml']))

    def test_sanitize_rel_path_colon_windows(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit:.\\test-results.xml'), ('xunit', ['.\\test-results.xml']))

    def test_sanitize_rel_path_semicolon_windows(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit;.\\test-results.xml'), ('xunit', ['.\\test-results.xml']))

    def test_sanitize_abs_path_colon_posix(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit:/home/test-results.xml'), ('xunit', ['/home/test-results.xml']))

    def test_sanitize_abs_path_semicolon_posix(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit;/home/test-results.xml'), ('xunit', ['/home/test-results.xml']))

    def test_sanitize_abs_path_colon_windows(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit:C:\\testResults\\test-results.xml'), ('xunit', ['C:\\testResults\\test-results.xml']))

    def test_sanitize_abs_path_semicolon_windows(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit;C:\\testResults\\test-results.xml'), ('xunit', ['C:\\testResults\\test-results.xml']))

    def test_sanitize_abs_rel_path_colon_posix(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit:/home/test-results.xml:./test-results.xml'),
                         ('xunit', ['/home/test-results.xml', './test-results.xml']))

    def test_sanitize_abs_rel_path_semicolon_posix(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit;/home/test-results.xml;./test-results.xml'),
                         ('xunit', ['/home/test-results.xml', './test-results.xml']))

    def test_sanitize_abs_rel_path_colon_windows(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit:C:\\home\\test-results.xml:.\\test-results.xml'),
                         ('xunit', ['C:\\home\\test-results.xml', '.\\test-results.xml']))

    def test_sanitize_abs_rel_path_semicolon_windows(self):
        output_choice = OutputChoice(['xunit'])
        self.assertEqual(output_choice.sanitize('xunit;C:\\home\\test-results.xml;.\\test-results.xml'),
                         ('xunit', ['C:\\home\\test-results.xml', '.\\test-results.xml']))
