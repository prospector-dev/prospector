from vulture import Vulture
from prospector.message import Location, Message
from prospector.tools.base import ToolBase


class ProspectorVulture(Vulture):

    def __init__(self, found_files):
        Vulture.__init__(self, exclude=None, verbose=False)
        self._files = found_files

    def scavenge(self, _=None):
        # The argument is a list of paths, but we don't care
        # about that as we use the found_files object. The
        # argument is here to explicitly acknowledge that we
        # are overriding the Vulture.scavenge method.
        for module in self._files.iter_module_paths():
            module_string = open(module).read()
            self.file = module
            self.scan(module_string)

    def get_messages(self):
        all_items = (
            ('unused-function', 'Unused function %s', self.unused_funcs),
            ('unused-property', 'Unused property %s', self.unused_props),
            ('unused-variable', 'Unused variable %s', self.unused_vars),
            ('unused-attribute', 'Unused attribute %s', self.unused_attrs)
        )

        messages = []
        for code, template, items in all_items:
            for item in items:
                loc = Location(item.file, None, None, item.lineno, -1)
                message_text = template % item
                message = Message('vulture', code, loc, message_text)
                messages.append(message)

        return messages


class VultureTool(ToolBase):
    def __init__(self):
        ToolBase.__init__(self)
        self._vulture = None

    def prepare(self, found_files, args, adaptors):
        self._vulture = ProspectorVulture(found_files)

    def run(self):
        self._vulture.scavenge()
        return self._vulture.get_messages()
