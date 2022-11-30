import mimetypes
from pathlib import Path

from dodgy.checks import check_file_contents

from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import ToolBase


def module_from_path(path: Path):
    # TODO hacky...
    return ".".join(path.parts[1:-1] + (path.stem,))


class DodgyTool(ToolBase):
    def configure(self, prospector_config, found_files):
        # empty: just implementing to satisfy the ABC contract
        pass

    def run(self, found_files: FileFinder):

        warnings = []
        for filepath in found_files.files:
            mimetype = mimetypes.guess_type(str(filepath.absolute()))
            if mimetype[0] is None or not mimetype[0].startswith("text/") or mimetype[1] is not None:
                continue
            try:
                contents = read_py_file(filepath)
            except CouldNotHandleEncoding:
                continue
            for line, code, message in check_file_contents(contents):
                warnings.append({"line": line, "code": code, "message": message, "path": filepath})

        messages = []
        for warning in warnings:
            path = warning["path"]
            loc = Location(path, module_from_path(path), "", warning["line"], 0)
            msg = Message("dodgy", warning["code"], loc, warning["message"])
            messages.append(msg)

        return messages
