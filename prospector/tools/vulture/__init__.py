# -*- coding: utf-8 -*-
from collections import namedtuple
from vulture import Vulture
from prospector.encoding import CouldNotHandleEncoding, read_py_file
from prospector.message import Location, Message, make_tool_error_message
from prospector.tools.base import ToolBase


_Item = namedtuple("_Item", "file lineno unused")


class ProspectorVulture(Vulture):

    def __init__(self, found_files):
        Vulture.__init__(self, exclude=None, verbose=False)
        self._files = found_files
        self._internal_messages = []
        self._all_unused_funcs = []
        self._all_unused_props = []
        self._all_unused_vars = []
        self._all_unused_attrs = []

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
            self.scan(module_string)

            self._all_unused_funcs.extend([_Item(self.file, 1, u)
                                           for u in self.unused_funcs])
            self._all_unused_props.extend([_Item(self.file, 1, u)
                                           for u in self.unused_props])
            self._all_unused_vars.extend([_Item(self.file, 1, u)
                                          for u in self.unused_vars])
            self._all_unused_attrs.extend([_Item(self.file, 1, u)
                                           for u in self.unused_attrs])

    def get_messages(self):
        all_items = (
            ('unused-function', 'Unused function %s', self._all_unused_funcs),
            ('unused-property', 'Unused property %s', self._all_unused_props),
            ('unused-variable', 'Unused variable %s', self._all_unused_vars),
            ('unused-attribute', 'Unused attribute %s', self._all_unused_attrs)
        )

        vulture_messages = []
        for code, template, items in all_items:
            for item in items:
                loc = Location(item.file, None, None, item.lineno, -1)
                message_text = template % item.unused
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
