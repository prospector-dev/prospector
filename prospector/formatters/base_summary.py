from prospector.formatters.base import Formatter


class SummaryFormatter(Formatter):
    """
    This abstract formatter is used to output a summary of the prospector run.
    """

    summary_labels = (
        ("started", "Started", None),
        ("completed", "Finished", None),
        ("time_taken", "Time Taken", lambda x: f"{x} seconds"),
        ("formatter", "Formatter", None),
        ("profiles", "Profiles", None),
        ("strictness", "Strictness", None),
        ("libraries", "Libraries Used", ", ".join),
        ("tools", "Tools Run", ", ".join),
        ("adaptors", "Adaptors", ", ".join),
        ("message_count", "Messages Found", None),
        ("external_config", "External Config", None),
    )

    def render_summary(self) -> str:
        output = [
            "Check Information",
            "=================",
        ]

        label_width = max(len(label[1]) for label in self.summary_labels)

        for key, label, formatter in self.summary_labels:
            if key in self.summary:
                value = self.summary[key]
                if formatter is not None:
                    value = formatter(value)
                output.append(f" {label.rjust(label_width)}: {value}")

        return "\n".join(output)

    def render_profile(self) -> str:
        output = ["Profile", "=======", "", self.profile.as_yaml().strip()]

        return "\n".join(output)
