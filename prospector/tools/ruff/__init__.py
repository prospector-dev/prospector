import json
import subprocess  # nosec
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ruff.__main__ import find_ruff_bin

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import PEP8_IGNORE_LINE_CODE, ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


class RuffTool(ToolBase):
    def configure(self, prospector_config: "ProspectorConfig", _: Any) -> None:
        self.ruff_bin = find_ruff_bin()
        self.ruff_args = ["check", "--output-format=json"]

        enabled = prospector_config.get_enabled_messages("ruff")
        if enabled:
            enabled_arg_value = ",".join(enabled)
            self.ruff_args.append(f"--select={enabled_arg_value}")
        disabled = prospector_config.get_disabled_messages("ruff")
        if disabled:
            disabled_arg_value = ",".join(disabled)
            self.ruff_args.append(f"--ignore={disabled_arg_value}")

        options = prospector_config.tool_options("ruff")
        for key, value in options.items():
            if value is True:
                self.ruff_args.append(f"--{key}")
            elif value is False:
                pass
            elif isinstance(value, list):
                arg_value = ",".join(value)
                self.ruff_args.append(f"--{key}={arg_value}")
            # dict is like array but with a dict with true/false value to be able to merge profiles
            elif isinstance(value, dict):
                arg_value = ",".join(k for k, v in value.items() if v)
                self.ruff_args.append(f"--{key}={arg_value}")
            else:
                self.ruff_args.append(f"--{key}={value}")

    def run(self, found_files: FileFinder) -> list[Message]:
        messages = []
        completed_process = subprocess.run(  # noqa
            [self.ruff_bin, *self.ruff_args, *found_files.python_modules], capture_output=True
        )
        if not completed_process.stdout:
            messages.append(
                Message(
                    "ruff",
                    "",
                    Location(None, None, None, None, None),
                    completed_process.stderr.decode(),
                )
            )
            return messages
        for message in json.loads(completed_process.stdout):
            sub_message = {}
            if message.get("fix") and message["fix"].get("applicability"):
                sub_message["Fix applicability"] = message["fix"]["applicability"]
            message_str = message.get("message", "")
            if sub_message:
                message_str += f" [{', '.join(f'{k}: {v}' for k, v in sub_message.items())}]"

            if message.get("filename") is None or found_files.is_excluded(Path(message.get("filename"))):
                continue
            messages.append(
                Message(
                    "ruff",
                    message.get("code") or "unknown",
                    Location(
                        message.get("filename") or "unknown",
                        None,
                        None,
                        line=message.get("location", {}).get("row"),
                        character=message.get("location", {}).get("column"),
                        line_end=message.get("end_location", {}).get("row"),
                        character_end=message.get("end_location", {}).get("column"),
                    ),
                    message_str,
                    doc_url=message.get("url"),
                    is_fixable=bool((message.get("fix") or {}).get("applicability") in ("safe", "unsafe")),
                )
            )
        return messages

    def get_ignored_codes(self, line: str) -> list[str]:
        match = PEP8_IGNORE_LINE_CODE.search(line)
        if match:
            return [e.strip() for e in match.group(1).split(",")]
        return []
