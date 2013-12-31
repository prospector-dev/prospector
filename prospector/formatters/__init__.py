from prospector.formatters import json, text, grouped

FORMATTERS = {
    'json': json.format_messages,
    'text': text.format_messages,
    'grouped': grouped.format_messages,
}
