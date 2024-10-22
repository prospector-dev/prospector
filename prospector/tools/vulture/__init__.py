from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vulture import Vulture

from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.finder import FileFinder
from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


class ProspectorVulture(Vulture):
    def __init__(self, found_files: FileFinder) -> None:
        Vulture.__init__(self, verbose=False)
        self._files = found_files
        self._internal_messages: list[Message] = []
        self.file: Optional[Path] = None
        self.filename: Optional[Path] = None

    def scavenge(self, _: Any = None, __: Any = None) -> None:
        # The argument is a list of paths, but we don't care
        # about that as we use the found_files object. The
        # argument is here to explicitly acknowledge that we
        # are overriding the Vulture.scavenge method.
        for module in self._files.python_modules:
            try:
                module_string = read_py_file(module)
            except CouldNotHandleEncoding as err:
                self._internal_messages.append(
                    make_tool_error_message(
                        module,
                        "vulture",
                        "V000",
                        message=(
                            f"Could not handle the encoding of this file: {err.encoding}"  # type: ignore[attr-defined]
                        ),
                    )
                )
                continue
            self.file = module
            self.filename = module
            try:
                self.scan(module_string, filename=module)
            except TypeError:
                self.scan(module_string)

    def get_messages(self) -> list[Message]:
        all_items = (
            ("unused-function", "Unused function %s", self.unused_funcs),
            ("unused-property", "Unused property %s", self.unused_props),
            ("unused-variable", "Unused variable %s", self.unused_vars),
            ("unused-attribute", "Unused attribute %s", self.unused_attrs),
        )

        vulture_messages = []
        for code, template, items in all_items:
            for item in items:
                try:
                    filename = item.file
                except AttributeError:
                    filename = item.filename
                lineno = item.lineno if hasattr(item, "lineno") else item.first_lineno
                loc = Location(filename, None, None, lineno, -1)
                message_text = template % item
                message = Message("vulture", code, loc, message_text)
                vulture_messages.append(message)

        return self._internal_messages + vulture_messages


class VultureTool(ToolBase):
    def __init__(self) -> None:
        ToolBase.__init__(self)
        self._vulture = None
        self.ignore_codes: list[str] = []

    def configure(  # pylint: disable=useless-return
        self, prospector_config: "ProspectorConfig", found_files: FileFinder
    ) -> Optional[tuple[Optional[str], Optional[Iterable[Message]]]]:
        self.ignore_codes = prospector_config.get_disabled_messages("vulture")
        return None

    def run(self, found_files: FileFinder) -> list[Message]:
        vulture = ProspectorVulture(found_files)
        vulture.scavenge()
        return [message for message in vulture.get_messages() if message.code not in self.ignore_codes]
