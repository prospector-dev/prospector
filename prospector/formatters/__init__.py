from prospector.formatters import json, text, grouped, emacs

FORMATTERS = {
    'json': json.format_messages,
    'text': text.format_messages,
    'grouped': grouped.format_messages,
    'emacs': emacs.format_messages
}
