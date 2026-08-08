from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from vulture import Vulture
from vulture.config import InputError, make_config

from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.finder import FileFinder
from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


class ProspectorVulture(Vulture):
    def __init__(
        self,
        found_files: FileFinder,
        ignore_names: list[str] | None = None,
        ignore_decorators: list[str] | None = None,
    ) -> None:
        Vulture.__init__(
            self,
            verbose=False,
            ignore_names=ignore_names,
            ignore_decorators=ignore_decorators,
        )
        self._files = found_files
        self._internal_messages: list[Message] = []
        self.file: Path | None = None
        self.filename: Path | None = None

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
        self.ignore_names: list[str] = []
        self.ignore_decorators: list[str] = []

    def configure(
        self, prospector_config: ProspectorConfig, found_files: FileFinder
    ) -> tuple[str | Path | None, Iterable[Message] | None] | None:
        self.ignore_codes = prospector_config.get_disabled_messages("vulture")

        if not prospector_config.use_external_config("vulture"):
            return None

        pyproject = Path(prospector_config.workdir) / "pyproject.toml"
        if not pyproject.exists():
            return None

        try:
            with pyproject.open("rb") as toml_file:
                config = make_config(argv=[str(prospector_config.workdir)], tomlfile=toml_file)
        except InputError as err:
            return pyproject, [
                make_tool_error_message(pyproject, "vulture", "V001", message=f"Invalid configuration: {err}")
            ]

        self.ignore_names = list(config["ignore_names"])
        self.ignore_decorators = list(config["ignore_decorators"])
        if not self.ignore_names and not self.ignore_decorators:
            # nothing in this pyproject.toml is relevant to vulture
            return None
        return pyproject, None

    def run(self, found_files: FileFinder) -> list[Message]:
        vulture = ProspectorVulture(found_files, self.ignore_names, self.ignore_decorators)
        vulture.scavenge()
        return [message for message in vulture.get_messages() if message.code not in self.ignore_codes]
