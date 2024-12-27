from prospector.formatters.text import TextFormatter
from prospector.message import Message

__all__ = ("EmacsFormatter",)


class EmacsFormatter(TextFormatter):
    def render_message(self, message: Message) -> str:
        output = [
            f"{self._make_path(message.location)}:{message.location.line}:{(message.location.character or 0) + 1}:",
            "    L{}:{} {}: {} - {}".format(
                message.location.line or "-",
                message.location.character if message.location.line else "-",
                message.location.function,
                message.source,
                message.code,
            ),
            f"    {message.message}",
        ]

        return "\n".join(output)
