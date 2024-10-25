from collections import defaultdict
from pathlib import Path

from prospector.formatters.text import TextFormatter
from prospector.message import Message

__all__ = ("GroupedFormatter",)


class GroupedFormatter(TextFormatter):
    def render_messages(self) -> str:
        output = [
            "Messages",
            "========",
            "",
        ]

        groups: dict[Path, dict[int, list[Message]]] = defaultdict(lambda: defaultdict(list))

        for message in self.messages:
            assert message.location.line is not None
            groups[self._make_path(message.location)][message.location.line].append(message)

        for filename in sorted(groups.keys()):
            output.append(str(filename))

            for line in sorted(groups[filename].keys(), key=lambda x: 0 if x is None else int(x)):
                output.append(f"  Line: {line}")

                for message in groups[filename][line]:
                    output.append(
                        "    {}: {} / {}{}".format(
                            message.source,
                            message.code,
                            message.message,
                            (f" (col {message.location.character})") if message.location.character else "",
                        )
                    )

            output.append("")

        return "\n".join(output)
