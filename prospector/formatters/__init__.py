# -*- coding: utf-8 -*-
from prospector.formatters import json, text, grouped, emacs, yaml, pylint, xunit, vscode


__all__ = (
    'FORMATTERS',
)


FORMATTERS = {
    'json': json.JsonFormatter,
    'text': text.TextFormatter,
    'grouped': grouped.GroupedFormatter,
    'emacs': emacs.EmacsFormatter,
    'yaml': yaml.YamlFormatter,
    'pylint': pylint.PylintFormatter,
    'xunit': xunit.XunitFormatter,
    'vscode': vscode.VSCodeFormatter,
}
