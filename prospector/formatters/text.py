from prospector.formatters.base_summary import SummaryFormatter
from prospector.message import Message

__all__ = ("TextFormatter",)


class TextFormatter(SummaryFormatter):
    def render_message(self, message: Message) -> str:
        output = []

        if message.location.module:
            output.append(f"{message.location.module} ({self._make_path(message.location)}):")
        else:
            output.append(f"{self._make_path(message.location)}:")

        output.append(
            "    L{}:{} {}: {} - {}".format(
                message.location.line or "-",
                message.location.character if message.location.character else "-",
                message.location.function,
                message.source,
                message.code,
            )
        )

        output.append(f"    {message.message}")

        return "\n".join(output)

    def render_messages(self) -> str:
        output = [
            "Messages",
            "========",
            "",
        ]

        for message in self.messages:
            output.append(self.render_message(message))
            output.append("")

        return "\n".join(output)

    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        output = []
        if messages and self.messages:  # if there are no messages, don't render an empty header
            output.append(self.render_messages())
        if profile:
            output.append(self.render_profile())
        if summary:
            output.append(self.render_summary())

        return "\n\n\n".join(output) + "\n"
