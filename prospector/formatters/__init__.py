# -*- coding: utf-8 -*-
from prospector.formatters import emacs, grouped, json, pylint, text, vscode, xunit, yaml

__all__ = ("FORMATTERS",)


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
