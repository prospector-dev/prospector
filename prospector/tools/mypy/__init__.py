from multiprocessing import Process, Queue

from mypy import api

from prospector.message import Location, Message
from prospector.tools import ToolBase

__all__ = ("MypyTool",)

from prospector.tools.exceptions import BadToolConfig


def format_message(message):
    try:
        (path, line, char, err_type, err_msg) = message.split(":", 4)
        line = int(line)
        character = int(char)
    except ValueError:
        try:
            (path, line, err_type, err_msg) = message.split(":", 3)
            line = int(line)
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


def _run_in_subprocess(q, cmd, paths):
    """
    This function exists only to be called by multiprocessing.Process as using
    lambda is forbidden
    """
    q.put(cmd(paths))


class MypyTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checker = api
        self.options = ["--show-column-numbers", "--no-error-summary"]
        self.use_dmypy = False

    def configure(self, prospector_config, _):
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

            raise BadToolConfig("mypy", f"The option {name} has an unsupported balue type: {type(value)}")

    def run(self, found_files):
        paths = [str(path) for path in found_files.python_modules]
        paths.extend(self.options)
        if self.use_dmypy:
            # Due to dmypy messing with stdout/stderr we call it in a separate
            # process
            q = Queue(1)
            p = Process(target=_run_in_subprocess, args=(q, self.checker.run_dmypy, ["run", "--"] + paths))
            p.start()
            result = q.get()
            p.join()
        else:
            result = self.checker.run(paths)
        report, _ = result[0], result[1:]  # noqa

        return [format_message(message) for message in report.splitlines()]
