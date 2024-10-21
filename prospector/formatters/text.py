from prospector.formatters.base_summary import SummaryFormatter

__all__ = ("TextFormatter",)


# pylint: disable=unnecessary-lambda


class TextFormatter(SummaryFormatter):

    def render_message(self, message):
        output = []

        if message.location.module:
            output.append(f"{message.location.module} ({self._make_path(message.location.path)}):")
        else:
            output.append("%s:" % self._make_path(message.location.path))

        output.append(
            "    L%s:%s %s: %s - %s"
            % (
                message.location.line or "-",
                message.location.character if message.location.character else "-",
                message.location.function,
                message.source,
                message.code,
            )
        )

        output.append("    %s" % message.message)

        return "\n".join(output)

    def render_messages(self):
        output = [
            "Messages",
            "========",
            "",
        ]

        for message in self.messages:
            output.append(self.render_message(message))
            output.append("")

        return "\n".join(output)

    def render_profile(self):
        output = ["Profile", "=======", "", self.profile.as_yaml().strip()]

        return "\n".join(output)

    def render(self, summary=True, messages=True, profile=False):
        output = []
        if messages and self.messages:  # if there are no messages, don't render an empty header
            output.append(self.render_messages())
        if profile:
            output.append(self.render_profile())
        if summary:
            output.append(self.render_summary())

        return "\n\n\n".join(output) + "\n"
