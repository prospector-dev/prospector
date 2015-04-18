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

    def test_sort_between_none_lines(self):

        locs = [
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 15, 0),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 0),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', -1, 0)
        ]

        lines = [(loc.line or -1) for loc in locs]
        expected = [None if l == -1 else l for l in sorted(lines)]

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

    def test_sort_between_none_chars(self):

        locs = [
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, -1),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 1),
            Location('/tmp/path/module1.py', 'module1', 'somefunc', 10, 2)
        ]

        chars = [(loc.character or -1) for loc in locs]
        expected = [None if c == -1 else c for c in sorted(chars)]

        self.assertEqual(expected, [loc.character for loc in sorted(locs)])
