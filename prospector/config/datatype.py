from os import pathsep

from setoptconf.datatype import Choice


class OutputChoice(Choice):
    def sanitize(self, value):
        splitted_value = value.split(pathsep)
        output_format, output_targets = splitted_value[0], splitted_value[1:]
        validated_format =  super(OutputChoice, self).sanitize(output_format)
        return (output_format, output_targets)