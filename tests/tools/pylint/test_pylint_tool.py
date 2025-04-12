import os
from collections.abc import Iterable
from pathlib import Path, PosixPath
from typing import Callable, Optional, Union
from unittest import TestCase
from unittest.mock import patch

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.message import Message
from prospector.tools.pylint import PylintTool

THIS_DIR = Path(__file__).parent


def _get_pylint_tool_and_prospector_config(
    argv_patch: Optional[list[str]] = None,
) -> tuple[PylintTool, ProspectorConfig]:
    if argv_patch is None:
        argv_patch = [""]
    with patch("sys.argv", argv_patch):
        config = ProspectorConfig()
    pylint_tool = PylintTool()
    return pylint_tool, config


def _get_test_files(
    *names: Union[str, Path], exclusion_filters: Optional[Iterable[Callable[[Path], bool]]] = None
) -> FileFinder:
    paths = [THIS_DIR / name for name in names]
    return FileFinder(*paths, exclusion_filters=exclusion_filters)


class TestPylintTool(TestCase):
    def test_checkpath_includes_no_init_modules(self) -> None:
        """
        If a subdirectory of a package has a .py file but no __init__.py it should still be included
        """
        files = _get_test_files("test_no_init_found")
        tool, config = _get_pylint_tool_and_prospector_config()
        del config
        check_paths = tool._get_pylint_check_paths(files)  # pylint: disable=protected-access
        assert len(check_paths) == 2
        assert sorted(Path(p).name for p in check_paths) == ["file3.py", "test_no_init_found"]

    def test_no_duplicates_in_checkpath(self) -> None:
        """
        This checks that the pylint tool will not generate a list of packages and subpackages -
        if there is a hierarchy there is no need to duplicate sub-packages in the list to be checked
        """
        root = THIS_DIR / "duplicates_test"
        files = FileFinder(root)
        tool, config = _get_pylint_tool_and_prospector_config()
        del config
        check_paths = tool._get_pylint_check_paths(files)  # pylint: disable=protected-access
        assert len(check_paths) == 1
        assert [str(Path(p).relative_to(root)) for p in check_paths] == ["pkg1"]

    def test_pylint_config(self) -> None:
        """Verifies that prospector will configure pylint with any pylint-specific configuration if found"""

        def _has_message(msg_list: list[Message], code: str) -> bool:
            return any(message.code == code and message.source == "pylint" for message in msg_list)

        for config_type in ("pylintrc", "pylintrc2", "pyproject", "setup.cfg"):
            root = THIS_DIR / "pylint_configs" / config_type

            with patch("pathlib.Path.cwd", return_value=root.absolute()):
                pylint_tool, config = _get_pylint_tool_and_prospector_config()
            assert Path(config.workdir).absolute() == root.absolute()

            found_files = _get_test_files(root)
            pylint_tool.configure(config, found_files)

            messages = pylint_tool.run(found_files)
            assert _has_message(messages, "line-too-long"), config_type

    def test_absolute_path_is_computed_correctly(self) -> None:
        pylint_tool, config = _get_pylint_tool_and_prospector_config()
        root = os.path.join(os.path.dirname(__file__), "testpath", "testfile.py")
        root_sep_split = root.split(os.path.sep)
        root_os_split = os.path.split(root)
        found_files = _get_test_files("testpath/testfile.py")
        pylint_tool.configure(config, found_files)
        assert pylint_tool._args != [os.path.join(*root_sep_split)]  # pylint: disable=protected-access
        assert pylint_tool._args == [PosixPath(os.path.join(*root_os_split))]  # pylint: disable=protected-access

    def test_wont_throw_false_positive_relative_beyond_top_level(self) -> None:
        with patch("os.getcwd", return_value=os.path.realpath("tests/tools/pylint/testpath/")):
            pylint_tool, config = _get_pylint_tool_and_prospector_config()
        found_files = _get_test_files("testpath/src/mcve/foobar.py")
        pylint_tool.configure(config, found_files)
        messages = pylint_tool.run(found_files)
        assert len(messages) == 0

    def test_will_throw_useless_suppression(self) -> None:
        with patch("os.getcwd", return_value=os.path.realpath("tests/tools/pylint/testpath/")):
            pylint_tool, config = _get_pylint_tool_and_prospector_config(argv_patch=["", "-t", "pylint"])

        found_files = _get_test_files("testpath", "testpath/test_useless_suppression.py")
        pylint_tool.configure(config, found_files)
        # useless-suppression is now disable by default in pylint
        assert pylint_tool._linter is not None  # pylint: disable=protected-access
        pylint_tool._linter.enable("useless-suppression")  # pylint: disable=protected-access
        messages = pylint_tool.run(found_files)
        assert any(m.code == "useless-suppression" for m in messages), (
            "There should be at least one useless suppression"
        )

    def test_parallel_execution(self) -> None:
        root = THIS_DIR / "parallel"

        with patch("pathlib.Path.cwd", return_value=root.absolute()):
            pylint_tool, config = _get_pylint_tool_and_prospector_config()
        assert Path(config.workdir).absolute() == root.absolute()

        found_files = _get_test_files(root, exclusion_filters=[config.make_exclusion_filter()])
        pylint_tool.configure(config, found_files)
        assert pylint_tool._linter is not None  # pylint: disable=protected-access
        assert pylint_tool._linter.config.jobs == 2  # pylint: disable=protected-access

        messages = pylint_tool.run(found_files)
        assert "line-too-long" in [msg.code for msg in messages if msg.source == "pylint"]

    def test_ignore_code(self) -> None:
        pylint_tool, _ = _get_pylint_tool_and_prospector_config()
        assert pylint_tool.get_ignored_codes("toto # pylint: disable=missing-docstring") == [("missing-docstring", 0)]
        assert pylint_tool.get_ignored_codes("toto # pylint: disable=missing-docstring # titi") == [
            ("missing-docstring", 0)
        ]
        assert pylint_tool.get_ignored_codes("toto # Pylint: Disable=missing-docstring") == [("missing-docstring", 0)]
        assert pylint_tool.get_ignored_codes("toto # pylint: disable=missing-docstring,invalid-name") == [
            ("missing-docstring", 0),
            ("invalid-name", 0),
        ]
        assert pylint_tool.get_ignored_codes("toto # pylint: disable=missing-docstring, invalid-name") == [
            ("missing-docstring", 0),
            ("invalid-name", 0),
        ]
        assert pylint_tool.get_ignored_codes("toto # pylint: disable-next=missing-docstring") == [
            ("missing-docstring", 1)
        ]
