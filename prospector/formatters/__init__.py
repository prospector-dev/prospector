from prospector.formatters import json, text, grouped, emacs, yaml


__all__ = (
    'FORMATTERS',
)


FORMATTERS = {
    'json': json.JsonFormatter,
    'text': text.TextFormatter,
    'grouped': grouped.GroupedFormatter,
    'emacs': emacs.EmacsFormatter,
    'yaml': yaml.YamlFormatter,
}
