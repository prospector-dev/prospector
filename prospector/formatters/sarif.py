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
        output: list[dict[str, Any]] = []

        if messages:
            for message in sorted(self.messages):
                output.append(
                    {
                        "ruleId": message.code,
                        "level": "warning",
                        "message": {
                            "text": f"{message.source}[{message.code}]: {message.message.strip()}"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": str(self._make_path(message.location))
                                    }
                                },
                                "region": {
                                    "startLine": message.location.line,
                                    "endLine": message.location.line_end,
                                    "startColumn": message.location.character,
                                    "endColumn": message.location.character_end
                                }
                            }
                        ]
                    }
                )

        sarif_skeleton = {
            "version": "2.1.0",
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Prospector",
                            "informationUri": "https://github.com/prospector-dev/prospector",
                            "version": _VERSION
                        }
                    }
                }
            ]
        }

        return json.dumps(sarif_skeleton, indent=2)
