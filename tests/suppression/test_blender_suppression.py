import unittest
from pathlib import Path

from prospector.suppression import Ignore, get_suppressions
from prospector.tools.base import ToolBase
from prospector.tools.mypy import MypyTool
from prospector.tools.pylint import PylintTool
from prospector.tools.ruff import RuffTool


class BlenderSuppressionsTest(unittest.TestCase):
    def test_blender_suppressions_pylint(self) -> None:
        path = Path(__file__).parent / "testdata" / "test_blender_suppressions" / "test.py"
        tools: dict[str, ToolBase] = {"pylint": PylintTool()}
        blend_combos = [[("pylint", "n2"), ("other", "o2")]]

        _, _, messages_to_ignore = get_suppressions([path], [], tools, blending=False, blend_combos=blend_combos)
        assert messages_to_ignore == {path: {1: {Ignore(None, "n1")}}}

        _, _, messages_to_ignore = get_suppressions([path], [], tools, blending=True, blend_combos=blend_combos)
        assert path in messages_to_ignore
        assert 2 in messages_to_ignore[path]
        assert messages_to_ignore[path][2] == {Ignore("pylint", "n2"), Ignore("other", "o2")}

    def test_blender_suppressions_mypy(self) -> None:
        path = Path(__file__).parent / "testdata" / "test_blender_suppressions" / "test.py"
        tools: dict[str, ToolBase] = {"mypy": MypyTool()}
        blend_combos = [[("mypy", "n3"), ("other", "o3")]]

        _, _, messages_to_ignore = get_suppressions([path], [], tools, blending=False, blend_combos=blend_combos)
        assert messages_to_ignore == {path: {1: {Ignore(None, "n1")}}}

        _, _, messages_to_ignore = get_suppressions([path], [], tools, blending=True, blend_combos=blend_combos)
        assert path in messages_to_ignore
        assert 3 in messages_to_ignore[path]
        assert messages_to_ignore[path][3] == {Ignore("mypy", "n3"), Ignore("other", "o3")}

    def test_blender_suppressions_ruff(self) -> None:
        path = Path(__file__).parent / "testdata" / "test_blender_suppressions" / "test.py"
        tools: dict[str, ToolBase] = {"ruff": RuffTool()}
        blend_combos = [[("ruff", "n1"), ("other", "o1")]]

        _, _, messages_to_ignore = get_suppressions([path], [], tools, blending=False, blend_combos=blend_combos)
        assert messages_to_ignore == {path: {1: {Ignore(None, "n1")}}}

        _, _, messages_to_ignore = get_suppressions([path], [], tools, blending=True, blend_combos=blend_combos)
        assert path in messages_to_ignore
        assert 1 in messages_to_ignore[path]
        assert messages_to_ignore[path][1] == {Ignore("ruff", "n1"), Ignore("other", "o1"), Ignore(None, "n1")}
