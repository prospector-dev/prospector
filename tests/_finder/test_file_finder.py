# import os
# from unittest import TestCase
#
# from prospector._finder import find_python
#
#
# class TestDataMixin:
#     def _assert_find_files(self, name, expected, explicit_file_mode=False):
#         root = os.path.join(os.path.dirname(__file__), "testdata", name)
#         files = find_python([], [root], explicit_file_mode=explicit_file_mode)
#
#         expected = [os.path.relpath(os.path.join(root, e).rstrip(os.path.sep)) for e in expected]
#         expected.append(files.rootpath)
#         actual = files.get_minimal_syspath()
#
#         expected.sort(key=lambda x: len(x))
#
#         self.assertEqual(actual, expected)
#
#
# class TestSysPath(TestDataMixin, TestCase):
#     def test1(self):
#         self._assert_find_files("test1", ["", "somedir"])
#
#     def test2(self):
#         self._assert_find_files("test2", [""])
#
#     def test3(self):
#         self._assert_find_files("test3", ["package"])
#
#
# class TestNodeModulesDetection(TestDataMixin, TestCase):
#     def test_skip_node_modules(self):
#         self._assert_find_files("test_node_modules", ["module1"])
