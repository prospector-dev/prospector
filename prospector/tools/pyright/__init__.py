import json
import subprocess

import pyright

from prospector.message import Location, Message
from prospector.tools import ToolBase

__all__ = ("PyrightTool",)

from prospector.tools.exceptions import BadToolConfig

VALID_OPTIONS = [
    "level",
    "project",
    "pythonplatform",
    "pythonversion",
    "skipunannotated",
    "typeshed-path",
    "venv-path",
]


def format_messages(json_encoded):
    json_decoded = json.loads(json_encoded)
    diagnostics = json_decoded.get("generalDiagnostics", [])
    messages = []
    for diag in diagnostics:
        start_range = diag.get("range", {}).get("start", {})
        location = Location(
            path=diag["file"],
            module=None,
            function=None,
            line=start_range.get("line", -1),
            character=start_range.get("character", -1),
        )
        messages.append(
            Message(source="pyright", code=diag.get("rule", ""), location=location, message=diag.get("message", ""))
        )

    return messages


class PyrightTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checker = pyright
        self.options = ["--outputjson"]

    def configure(self, prospector_config, _):
        options = prospector_config.tool_options("pyright")

        for option_key in options.keys():
            if option_key not in VALID_OPTIONS:
                url = "https://github.com/PyCQA/prospector/blob/master/prospector/tools/pyright/__init__.py"
                raise BadToolConfig(
                    "pyright", f"Option {option_key} is not valid. " f"See the list of possible options: {url}"
                )

        level = options.get("level", None)
        project = options.get("project", None)
        pythonplatform = options.get("pythonplatform", None)
        pythonversion = options.get("pythonversion", None)
        skipunannotated = options.get("skipunannotated", False)
        typeshed_path = options.get("typeshed-path", None)
        venv_path = options.get("venv-path", None)

        if level:
            self.options.extend(["--level", level])
        if project:
            self.options.extend(["--project", project])
        if pythonplatform:
            self.options.extend(["--pythonplatform", pythonplatform])
        if pythonversion:
            self.options.extend(["--pythonversion", pythonversion])
        if skipunannotated:
            self.options.append("--skipunannotated")
        if typeshed_path:
            self.options.extend(["--typeshed-path", typeshed_path])
        if venv_path:
            self.options.extend(["--venv-path", venv_path])

    def run(self, found_files):
        paths = [str(path) for path in found_files.python_modules]
        paths.extend(self.options)
        result = self.checker.run(*paths, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        return format_messages(result.stdout)
