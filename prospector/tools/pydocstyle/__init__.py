from typing import TYPE_CHECKING, Any

from pydocstyle.checker import AllError, ConventionChecker

from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.finder import FileFinder
from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


__all__ = ("PydocstyleTool",)


class PydocstyleTool(ToolBase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._code_files: list[str] = []
        self.ignore_codes: list[str] = []

    def configure(self, prospector_config: "ProspectorConfig", found_files: FileFinder) -> None:
        self.ignore_codes = prospector_config.get_disabled_messages("pydocstyle")

    def run(self, found_files: FileFinder) -> list[Message]:
        messages = []

        checker = ConventionChecker()

        for code_file in found_files.python_modules:
            try:
                for error in checker.check_source(read_py_file(code_file), str(code_file.absolute()), None):
                    location = Location(path=code_file, module=None, function="", line=error.line, character=0)
                    message = Message(
                        source="pydocstyle",
                        code=error.code,
                        location=location,
                        message=error.message.partition(":")[2].strip(),
                    )
                    messages.append(message)
            except CouldNotHandleEncoding as err:
                messages.append(
                    make_tool_error_message(
                        code_file,
                        "pydocstyle",
                        "D000",
                        message=f"Could not handle the encoding of this file: {err.__cause__}",
                    )
                )
                continue
            except AllError as exc:
                # pydocstyle's Parser.parse_all method raises AllError when an
                # attempt to analyze the __all__ definition has failed.  This
                # occurs when __all__ is too complex to be parsed.
                messages.append(
                    make_tool_error_message(
                        code_file,
                        "pydocstyle",
                        "D000",
                        line=1,
                        character=0,
                        message=exc.args[0],
                    )
                )
                continue

        return self.filter_messages(messages)

    def filter_messages(self, messages: list[Message]) -> list[Message]:
        return [message for message in messages if message.code not in self.ignore_codes]
