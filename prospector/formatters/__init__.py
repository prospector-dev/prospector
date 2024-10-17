from enum import Enum

from . import emacs, grouped, json, pylint, text, vscode, xunit, yaml
from .base import Formatter

__all__ = ["Formatters", "Formatter", "FORMATTERS"]


FORMATTERS = {
    "json": json.JsonFormatter,
    "text": text.TextFormatter,
    "grouped": grouped.GroupedFormatter,
    "emacs": emacs.EmacsFormatter,
    "yaml": yaml.YamlFormatter,
    "pylint": pylint.PylintFormatter,
    "xunit": xunit.XunitFormatter,
    "vscode": vscode.VSCodeFormatter,
}
Formatters = Enum("Formatters", FORMATTERS)
