from . import emacs, gitlab, grouped, json, pylint, pylint_parseable, text, vscode, xunit, yaml
from .base import Formatter

__all__ = ("FORMATTERS", "Formatter")


FORMATTERS: dict[str, type[Formatter]] = {
    "json": json.JsonFormatter,
    "text": text.TextFormatter,
    "gitlab": gitlab.GitlabFormatter,
    "grouped": grouped.GroupedFormatter,
    "emacs": emacs.EmacsFormatter,
    "yaml": yaml.YamlFormatter,
    "pylint": pylint.PylintFormatter,
    "pylint_parseable": pylint_parseable.PylintParseableFormatter,
    "xunit": xunit.XunitFormatter,
    "vscode": vscode.VSCodeFormatter,
}
