from typing import Any

import yaml

from prospector.formatters.base import Formatter

__all__ = ("YamlFormatter",)


class YamlFormatter(Formatter):
    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        output: dict[str, Any] = {}

        if summary:
            output["summary"] = self.summary

        if profile:
            output["profile"] = self.profile.as_dict()

        if messages:
            output["messages"] = [self._message_to_dict(m) for m in self.messages]

        return yaml.safe_dump(
            output,
            indent=2,
            default_flow_style=False,
            allow_unicode=True,
        )
