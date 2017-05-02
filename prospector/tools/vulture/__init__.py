# -*- coding: utf-8 -*-
from vulture import Vulture
from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase


class ProspectorVulture(Vulture):

    def __init__(self, found_files):
        Vulture.__init__(self, exclude=None, verbose=False)
        self._files = found_files
        self._internal_messages = []

    def scavenge(self, _=None):
        # The argument is a list of paths, but we don't care
        # about that as we use the found_files object. The
        # argument is here to explicitly acknowledge that we
        # are overriding the Vulture.scavenge method.
        for module in self._files.iter_module_paths():
            try:
                module_string = read_py_file(module)
            except CouldNotHandleEncoding as err:
                self._internal_messages.append(make_tool_error_message(
                    module, 'vulture', 'V000',
                    message='Could not handle the encoding of this file: %s' % err.encoding
                ))
                continue
            self.file = module
            self.filename = module
            try:
                self.scan(module_string, filename=module)
            except TypeError:
                self.scan(module_string)

    def get_messages(self):
        all_items = (
            ('unused-function', 'Unused function %s', self.unused_funcs),
            ('unused-property', 'Unused property %s', self.unused_props),
            ('unused-variable', 'Unused variable %s', self.unused_vars),
            ('unused-attribute', 'Unused attribute %s', self.unused_attrs)
        )

        vulture_messages = []
        for code, template, items in all_items:
            for item in items:
                try:
                    filename = item.file
                except AttributeError:
                    filename = item.filename
                loc = Location(filename, None, None, item.lineno, -1)
                message_text = template % item
                message = Message('vulture', code, loc, message_text)
                vulture_messages.append(message)

        return self._internal_messages + vulture_messages


class VultureTool(ToolBase):
    def __init__(self):
        ToolBase.__init__(self)
        self._vulture = None
        self.ignore_codes = ()

    def configure(self, prospector_config, found_files):
        self.ignore_codes = prospector_config.get_disabled_messages('vulture')

    def run(self, found_files):
        vulture = ProspectorVulture(found_files)
        vulture.scavenge()
        return [message
                for message in vulture.get_messages()
                if message.code not in self.ignore_codes]
