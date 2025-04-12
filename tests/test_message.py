from pathlib import Path
from unittest import TestCase

import pytest

from prospector.message import Location


class LocationPathTest(TestCase):
    def test_paths(self) -> None:
        """
        Tests the absolute and relative path conversion
        """
        root = Path(__file__).parent.parent
        loc = Location(__file__, "module", "func", 1, 2)
        assert loc.relative_path(root) == Path("tests/test_message.py")
        absolute = root / "tests/test_message.py"
        assert loc.absolute_path() == absolute

    def test_strings_or_paths(self) -> None:
        """
        For ease of use the Location object can accept a path as a Path or a string
        """
        assert (
            Location("/tmp/path/module1.py", "module1", "somefunc", 12, 2)  # noqa: S108
            == Location(Path("/tmp/path/module1.py"), "module1", "somefunc", 12, 2)  # noqa: S108
        )

    def test_bad_path_input(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            Location(3.2, "module", "func", 1, 2)  # type: ignore[arg-type,unused-ignore]


class LocationOrderTest(TestCase):
    def test_path_order(self) -> None:
        locs = [
            Location(Path("/tmp/path/module3.py"), "module3", "somefunc", 15, 0),  # noqa: S108
            Location(Path("/tmp/path/module1.py"), "module1", "somefunc", 10, 0),  # noqa: S108
            Location("/tmp/path/module2.py", "module2", "somefunc", 9, 0),  # noqa: S108
        ]

        paths = [loc.path for loc in locs if loc.path is not None]
        expected = sorted(paths)

        assert expected == [loc.path for loc in sorted(locs)]

    def test_line_order(self) -> None:
        locs = [
            Location("/tmp/path/module1.py", "module1", "somefunc", 15, 0),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 0),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 12, 0),  # noqa: S108
        ]

        lines = [loc.line for loc in locs if loc.line is not None]
        expected = sorted(lines)

        assert expected == [loc.line for loc in sorted(locs)]

    def test_sort_between_none_lines(self) -> None:
        locs = [
            Location("/tmp/path/module1.py", "module1", "somefunc", 15, 0),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 0),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", -1, 0),  # noqa: S108
        ]

        lines = [(loc.line or -1) for loc in locs]
        expected = [None if line == -1 else line for line in sorted(lines)]

        assert expected == [loc.line for loc in sorted(locs)]

    def test_char_order(self) -> None:
        locs = [
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 7),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 0),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 2),  # noqa: S108
        ]

        chars = [loc.character for loc in locs if loc.character is not None]
        expected = sorted(chars)

        assert expected == [loc.character for loc in sorted(locs)]

    def test_sort_between_none_chars(self) -> None:
        locs = [
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, -1),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 1),  # noqa: S108
            Location("/tmp/path/module1.py", "module1", "somefunc", 10, 2),  # noqa: S108
        ]

        chars = [(loc.character or -1) for loc in locs]
        expected = [None if c == -1 else c for c in sorted(chars)]

        assert expected == [loc.character for loc in sorted(locs)]
