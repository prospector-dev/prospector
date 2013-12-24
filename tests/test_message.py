from unittest import TestCase
from prospector.message import Location


class LocationOrderTest(TestCase):

    def test_path_order(self):

        locs = [
            Location('/tmp/path/module3.py', 'module3', 'somefunc', 15, 0),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 0),
            Location('/tmp/path/module2.py', 'module2', 'somefunc', 9, 0)
        ]

        paths = [loc.path for loc in locs]
        expected = sorted(paths)

        self.assertEqual(expected, [loc.path for loc in sorted(locs)])

    def test_line_order(self):

        locs = [
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 15, 0),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 0),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 12, 0)
        ]

        lines = [loc.line for loc in locs]
        expected = sorted(lines)

        self.assertEqual(expected, [loc.line for loc in sorted(locs)])

    def test_char_order(self):

        locs = [
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 7),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 0),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 2)
        ]

        chars = [loc.character for loc in locs]
        expected = sorted(chars)

        self.assertEqual(expected, [loc.character for loc in sorted(locs)])