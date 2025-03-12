import os
from pathlib import Path
from typing import Optional

from prospector.formatters.base import Formatter
from prospector.message import Location, Message


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

    def get_ci_annotation(self, message: Message) -> Optional[str]:
        intro = (
            f"({message.source})"
            if message.code is None
            else f"{message.code}({message.source})"
            if message.location.function is None
            else f"[{message.code}({message.source}), {message.location.function}]"
        )
        ci_prefix = self._get_ci_prefix(message.location, intro)
        if ci_prefix:
            github_message = f"{ci_prefix}{intro}%0A{message.message.strip()}"
            if message.doc_url:
                github_message += f"%0ASee: {message.doc_url}"
            return github_message
        return None

    def _get_ci_prefix(self, location: Location, title: str) -> Optional[str]:
        if location.path is None:
            return None
        if os.environ.get("GITHUB_ACTIONS") == "true":
            path = location.path
            if "PROSPECTOR_FILE_PREFIX" in os.environ:
                path = Path(os.environ["PROSPECTOR_FILE_PREFIX"]) / path
            # pylint: disable-next=line-too-long
            # See: https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#setting-an-error-message
            parameters = {
                "file": path,
                "line": location.line,
                "title": title,
            }
            if location.line_end:
                parameters["endLine"] = location.line_end
            if location.character:
                parameters["col"] = location.character
            if location.character_end:
                parameters["endColumn"] = location.character_end

            parameters_str = ",".join(f"{key}={value}" for key, value in parameters.items())
            return f"::error {parameters_str}::"

        return None
