import os
import re
import sys


def parse_output_format(value: str) -> tuple[str, list[str]]:
    parsed = re.split(r"[;:]", value)
    output_format, output_targets = parsed[0], parsed[1:]
    checked_targets: list[str] = []
    for target in output_targets:
        if sys.platform.startswith("win") and target.startswith((os.path.sep, os.path.altsep)):
            checked_targets[-1] += ":" + target
        else:
            checked_targets.append(target)
    return output_format, checked_targets
