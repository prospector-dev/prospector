import os
from unittest import TestCase
from prospector.tools.pylint import _find_package_paths


class TestPylintTool(TestCase):

    def test_find_packages(self):
        root = os.path.join(os.path.dirname(__file__), 'package_test')
        sys_paths, check_paths = _find_package_paths(root)

        expected_checks = [os.path.join(os.path.dirname(__file__), p)
                           for p in ('package_test/package1', 'package_test/somedir/package2')]
        expected_sys_paths = [os.path.join(os.path.dirname(__file__), p)
                              for p in ('package_test', 'package_test/somedir')]

        sys_paths = list(sys_paths)

        sys_paths.sort()
        check_paths.sort()
        expected_checks.sort()
        expected_sys_paths.sort()

        self.assertEqual(expected_sys_paths, sys_paths)
        self.assertEqual(expected_checks, check_paths)