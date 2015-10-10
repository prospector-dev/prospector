from prospector.formatters.text import TextFormatter


__all__ = (
    'EmacsFormatter',
)


class EmacsFormatter(TextFormatter):
    def render_message(self, message):
        output = [
            '%s:%s:%d:' % (
                message.location.path,
                message.location.line,
                (message.location.character or 0) + 1,
            ),
            '    L%s:%s %s: %s - %s' % (
                message.location.line or '-',
                message.location.character if message.location.line else '-',
                message.location.function,
                message.source,
                message.code,
            ),
            '    %s' % message.message
        ]

        return '\n'.join(output)
