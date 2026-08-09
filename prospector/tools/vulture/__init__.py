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


def _pyproject_settings(workdir: Path) -> dict[str, Any]:
    """
    Read the `[tool.vulture]` section of the project's pyproject.toml.

    Vulture reads this section itself when it is run from the command line, so
    without it a project that configures `ignore_decorators` gets different
    results depending on whether it ran vulture or prospector. See #505.

    A missing or unreadable file means no settings, not an error: prospector
    runs in plenty of projects that have neither.
    """
    pyproject = workdir / "pyproject.toml"
    if not pyproject.is_file():
        return {}

    try:
        with pyproject.open("rb") as handle:
            # `argv` is only there to satisfy vulture's own argument parser,
            # which insists on a path; the paths it produces are unused, as
            # prospector has already found the files itself.
            return make_config(argv=[str(workdir)], tomlfile=handle)
    except (InputError, OSError, ValueError):
        return {}


class ProspectorVulture(Vulture):
    def __init__(
        self,
        found_files: FileFinder,
        ignore_names: list[str] | None = None,
        ignore_decorators: list[str] | None = None,
    ) -> None:
        Vulture.__init__(self, verbose=False, ignore_names=ignore_names, ignore_decorators=ignore_decorators)
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

    def configure(  # pylint: disable=useless-return
        self, prospector_config: ProspectorConfig, found_files: FileFinder
    ) -> tuple[str | None, Iterable[Message] | None] | None:
        self.ignore_codes = prospector_config.get_disabled_messages("vulture")

        settings = _pyproject_settings(prospector_config.workdir)
        self.ignore_names = settings.get("ignore_names", [])
        self.ignore_decorators = settings.get("ignore_decorators", [])
        return None

    def run(self, found_files: FileFinder) -> list[Message]:
        vulture = ProspectorVulture(
            found_files,
            ignore_names=self.ignore_names,
            ignore_decorators=self.ignore_decorators,
        )
        vulture.scavenge()
        return [message for message in vulture.get_messages() if message.code not in self.ignore_codes]
