import os
import re
import sys

from setoptconf.datatype import Choice


class OutputChoice(Choice):
    def sanitize(self, value: str) -> tuple[str, list[str]]:
        parsed = re.split(r"[;:]", value)
        output_format, output_targets = parsed[0], parsed[1:]
        checked_targets = []
        for target in output_targets:
            if sys.platform.startswith("win") and target.startswith((os.path.sep, os.path.altsep)):
                checked_targets[-1] += ":" + target
            else:
                checked_targets.append(target)
        validated_format = super().sanitize(output_format)
        return validated_format, checked_targets
