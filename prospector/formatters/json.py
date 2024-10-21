import json
from datetime import datetime
from typing import Any

from prospector.formatters.base import Formatter

__all__ = ("JsonFormatter",)


class JsonFormatter(Formatter):
    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        output: dict[str, Any] = {}

        if summary:
            # we need to slightly change the types and format
            # of a few of the items in the summary to make
            # them play nice with JSON formatting
            munged = {}
            for key, value in self.summary.items():
                if isinstance(value, datetime):
                    munged[key] = str(value)
                else:
                    munged[key] = value
            output["summary"] = munged

        if profile:
            output["profile"] = self.profile.as_dict()

        if messages:
            output["messages"] = [self._message_to_dict(m) for m in self.messages]

        return json.dumps(output, indent=2)
