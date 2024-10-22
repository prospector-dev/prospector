import codecs
import os
import re
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from pep8ext_naming import NamingChecker
from pycodestyle import PROJECT_CONFIG, USER_CONFIG, BaseReport, StyleGuide, register_check

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig

__all__ = ("PycodestyleTool",)


class ProspectorReport(BaseReport):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._prospector_messages: list[Message] = []

    def error(self, line_number: Optional[int], offset: int, text: str, check: str) -> None:
        code = super().error(
            line_number,
            offset,
            text,
            check,
        )
        if code is None:
            # The error pycodestyle found is being ignored, let's move on.
            return

        # Get a clean copy of the message text without the code embedded.
        text = text[5:]

        # mixed indentation (E101) is a file global message
        if code == "E101":
            line_number = None

        # Record the message using prospector's data structures.
        location = Location(
            path=self.filename,
            module=None,
            function=None,
            line=line_number,
            character=(offset + 1),
        )
        message = Message(
            # TODO: legacy output naming
            source="pycodestyle",
            code=code,
            location=location,
            message=text,
        )

        self._prospector_messages.append(message)

    def get_messages(self) -> list[Message]:
        return self._prospector_messages


class ProspectorStyleGuide(StyleGuide):
    def __init__(self, config: "ProspectorConfig", found_files: FileFinder, *args: Any, **kwargs: Any) -> None:
        self._config = config
        self._files = found_files
        self._module_paths = found_files.python_modules

        # Override the default reporter with our custom one.
        kwargs["reporter"] = ProspectorReport

        super().__init__(*args, **kwargs)

    def excluded(self, filename: str, parent: Optional[str] = None) -> bool:
        if super().excluded(filename, parent):
            return True

        # If the file survived pycodestyle's exclusion rules, check it against
        # prospector's patterns.
        fullpath = self._config.workdir / (parent or "") / filename
        if fullpath.is_dir():
            return False

        return fullpath not in self._module_paths


class PycodestyleTool(ToolBase):
    checker: Optional[ProspectorStyleGuide] = None

    def configure(
        self, prospector_config: "ProspectorConfig", found_files: FileFinder
    ) -> Optional[tuple[Optional[str], Optional[Iterable[Message]]]]:
        # figure out if we should use a pre-existing config file
        # such as setup.cfg or tox.ini
        external_config = None

        # 'none' means we ignore any external config, so just carry on
        use_config = False

        if prospector_config.use_external_config("pycodestyle"):
            use_config = True

            paths: list[Union[str, Path]] = [os.path.join(prospector_config.workdir, name) for name in PROJECT_CONFIG]
            paths.append(USER_CONFIG)
            ext_loc = prospector_config.external_config_location("pycodestyle")
            if ext_loc is not None:
                paths = [ext_loc] + paths  # type: ignore[assignment,operator]

            for conf_path in paths:
                if os.path.exists(conf_path) and os.path.isfile(conf_path):
                    # this file exists - but does it have pep8 or pycodestyle config in it?
                    # TODO: Remove this
                    header = re.compile(r"\[(pep8|pycodestyle)\]")
                    with codecs.open(str(conf_path)) as conf_file:
                        if any(header.search(line) for line in conf_file.readlines()):
                            external_config = conf_path
                            break

        # need to convert to strings rather than Path objects for compatibility with pycodestyle
        check_paths = [str(f.absolute()) for f in found_files.python_modules]

        # check_paths = [found_files.to_absolute_path(p) for p in check_paths]

        # Instantiate our custom pycodestyle checker.
        self.checker = ProspectorStyleGuide(
            config=prospector_config, paths=check_paths, found_files=found_files, config_file=external_config
        )
        if not use_config or external_config is None:
            configured_by = None
            # This means that we don't have existing config to use.
            # Make sure pycodestyle's code ignores are fully reset to zero before
            # adding prospector-flavoured configuration.
            self.checker.options.select = ()
            self.checker.options.ignore = tuple(prospector_config.get_disabled_messages("pycodestyle"))

            if "max-line-length" in prospector_config.tool_options("pycodestyle"):
                self.checker.options.max_line_length = prospector_config.tool_options("pycodestyle")["max-line-length"]
        else:
            configured_by = f"Configuration found at {external_config}"

        # if we have a command line --max-line-length argument, that
        # overrules everything
        max_line_length = prospector_config.max_line_length
        if max_line_length is not None:
            self.checker.options.max_line_length = max_line_length

        return configured_by, []

    def run(self, _: Any) -> list[Message]:
        assert self.checker is not None
        report = self.checker.check_files()
        return report.get_messages()


# Load pep8ext_naming into pycodestyle's configuration.
register_check(NamingChecker)
