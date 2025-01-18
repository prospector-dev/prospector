from multiprocessing import Process, Queue
from typing import TYPE_CHECKING, Any, Callable, Optional

from mypy import api

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools import ToolBase

__all__ = ("MypyTool",)

from prospector.tools.exceptions import BadToolConfig

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


def format_message(message: str) -> Message:
    character: Optional[int]
    try:
        (path, line_str, char_str, err_type, err_msg) = message.split(":", 4)
        line = int(line_str)
        character = int(char_str)
    except ValueError:
        try:
            (path, line_str, err_type, err_msg) = message.split(":", 3)
            line = int(line_str)
            character = None
        except ValueError:
            (path, err_type, err_msg) = message.split(":", 2)
            line = 0
            character = None
    location = Location(
        path=path,
        module=None,
        function=None,
        line=line,
        character=character,
    )
    return Message(
        source="mypy",
        code=err_type.lstrip(" "),
        location=location,
        message=err_msg.lstrip(" "),
    )


def _run_in_subprocess(
    q: "Queue[tuple[str, str]]", cmd: Callable[[list[str]], tuple[str, str]], paths: list[str]
) -> None:
    """
    This function exists only to be called by multiprocessing.Process as using
    lambda is forbidden
    """
    q.put(cmd(paths))


class MypyTool(ToolBase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.checker = api
        self.options = ["--show-column-numbers", "--no-error-summary"]
        self.use_dmypy = False

    def configure(self, prospector_config: "ProspectorConfig", _: Any) -> None:
        options = prospector_config.tool_options("mypy")

        self.use_dmypy = options.pop("use-dmypy", False)

        # For backward compatibility
        if "follow-imports" not in options:
            options["follow-imports"] = "normal"
        if "python-2-mode" in options and "py2" not in options:
            options["py2"] = options.pop("python-2-mode")

        for name, value in options.items():
            if value is False:
                continue
            if value is True:
                self.options.append(f"--{name}")
                continue
            if isinstance(value, (int, float, str)):
                self.options.append(f"--{name}={value}")
                continue
            if isinstance(value, list):
                for v in value:
                    self.options.append(f"--{name}-{v}")
                continue

            raise BadToolConfig("mypy", f"The option {name} has an unsupported value type: {type(value)}")

    def run(self, found_files: FileFinder) -> list[Message]:
        paths = [str(path) for path in found_files.python_modules]
        paths.extend(self.options)
        if self.use_dmypy:
            # Due to dmypy messing with stdout/stderr we call it in a separate
            # process
            q: Queue[str] = Queue(1)
            p = Process(target=_run_in_subprocess, args=(q, self.checker.run_dmypy, ["run", "--"] + paths))
            p.start()
            result = q.get()
            p.join()
        else:
            result = self.checker.run(paths)
        report, _ = result[0], result[1:]  # noqa

        return [format_message(message) for message in report.splitlines()]
