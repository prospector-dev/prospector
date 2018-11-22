import re

from setoptconf.datatype import Choice


class OutputChoice(Choice):
    def sanitize(self, value):
        parsed = re.split(r'[;:]', value)
        output_format, output_targets = parsed[0], parsed[1:]
        validated_format =  super(OutputChoice, self).sanitize(output_format)
        return (output_format, output_targets)
