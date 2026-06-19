import importlib
import json
from typing import Any

from prospector.formatters.base import Formatter

__all__ = ("SarifFormatter",)

_VERSION = importlib.metadata.version("prospector")


class SarifFormatter(Formatter):
    """
    This formatter outputs messages in the SARIF format.
    https://www.oasis-open.org/committees/sarif/charter.php
    """

    def render(self, summary: bool = True, messages: bool = True, profile: bool = False) -> str:
        results: list[dict[str, Any]] = []

        if messages:
            for message in sorted(self.messages):
                region: dict[str, int] = {}
                if message.location.line:
                    region["startLine"] = message.location.line
                if message.location.line_end:
                    region["endLine"] = message.location.line_end
                if message.location.character:
                    region["startColumn"] = message.location.character
                if message.location.character_end:
                    region["endColumn"] = message.location.character_end

                results.append(
                    {
                        "ruleId": message.code,
                        "level": "warning",
                        "message": {"text": f"{message.source}[{message.code}]: {message.message.strip()}"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": str(self._make_path(message.location))},
                                    "region": region,
                                }
                            }
                        ],
                    }
                )

        output = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Prospector",
                            "informationUri": "https://github.com/prospector-dev/prospector",
                            "version": _VERSION,
                        }
                    },
                    "results": results,
                }
            ],
        }

        return json.dumps(output, indent=2)
