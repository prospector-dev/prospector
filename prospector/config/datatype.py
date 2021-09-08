import os
import re
import sys

from setoptconf.datatype import Choice


class OutputChoice(Choice):
    def sanitize(self, value):
        parsed = re.split(r"[;:]", value)
        output_format, output_targets = parsed[0], parsed[1:]
        checked_targets = []
        for i, target in enumerate(output_targets):
            if sys.platform.startswith("win") and target.startswith((os.path.sep, os.path.altsep)):
                checked_targets[-1] += ":" + target
            else:
                checked_targets.append(target)
        validated_format = super(OutputChoice, self).sanitize(output_format)
        return (validated_format, checked_targets)
