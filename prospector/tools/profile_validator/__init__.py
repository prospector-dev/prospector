import re
import sre_constants
import yaml
from prospector.message import Location, Message
from prospector.profiles import AUTO_LOADED_PROFILES
from prospector.tools import ToolBase


CONFIG_SETTING_SHOULD_BE_LIST = 'should-be-list'
CONFIG_UNKNOWN_SETTING = 'unknown-setting'
CONFIG_SETTING_MUST_BE_INTEGER = 'should-be-int'
CONFIG_SETTING_MUST_BE_BOOL = 'should-be-bool'
CONFIG_INVALID_VALUE = 'invalid-value'
CONFIG_INVALID_REGEXP = 'invalid-regexp'
CONFIG_DEPRECATED_SETTING = 'deprecated'


class ProfileValidationTool(ToolBase):

    LIST_SETTINGS = (
        'inherits', 'uses', 'ignore', 'ignore-paths', 'ignore-patterns'
    )
    ALL_SETTINGS = LIST_SETTINGS + (
        'strictness', 'autodetect', 'max-line-length',
        'output-format', 'doc-warnings', 'test-warnings',
        'requirements',  # bit of a grim hack; prospector does not use this but Landscape does
    )

    def __init__(self):
        self.to_check = set(AUTO_LOADED_PROFILES)
        self.ignore_codes = ()

    def configure(self, prospector_config, found_files):
        for profile in prospector_config.config.profiles:
            self.to_check.add(profile)

        self.ignore_codes = prospector_config.get_disabled_messages('profile-validator')

    def tool_names(self):
        # TODO: this is currently a circular import, which is why it is not at the top of
        # the module. However, there's no obvious way to get around this right now...
        # pylint: disable=cyclic-import
        from prospector.tools import TOOLS
        return TOOLS.keys()

    def validate(self, filepath):
        messages = []

        with open(filepath) as profile_file:
            raw_contents = profile_file.read()
            parsed = yaml.safe_load(raw_contents)
            raw_contents = raw_contents.split('\n')

        def add_message(code, message, setting):
            if code in self.ignore_codes:
                return
            line = -1
            for number, fileline in enumerate(raw_contents):
                if setting in fileline:
                    line = number + 1
                    break
            location = Location(filepath, None, None, line, 0, False)
            message = Message('profile-validator', code, location, message)
            messages.append(message)

        for setting in ('doc-warnings', 'test-warnings', 'autodetect'):
            if not isinstance(parsed.get(setting, False), bool):
                add_message(CONFIG_SETTING_MUST_BE_BOOL, '"%s" should be true or false' % setting, setting)

        if not isinstance(parsed.get('max-line-length', 0), int):
            add_message(CONFIG_SETTING_MUST_BE_INTEGER, '"max-line-length" should be an integer', 'max-line-length')

        if 'strictness' in parsed:
            possible = ('veryhigh', 'high', 'medium', 'low', 'verylow')
            if parsed['strictness'] not in possible:
                add_message(CONFIG_INVALID_VALUE, '"strictness" must be one of %s' % ', '.join(possible), 'strictness')

        if 'uses' in parsed:
            possible = ('django', 'celery')
            for uses in parsed['uses']:
                if uses not in possible:
                    add_message(CONFIG_INVALID_VALUE,
                                '"%s" is not valid for "uses", must be one of %s' % (uses, ', '.join(possible)),
                                uses)

        if 'ignore' in parsed:
            add_message(CONFIG_DEPRECATED_SETTING,
                        '"ignore" is deprecated, please update to use "ignore-patterns" instead',
                        'ignore')

        for pattern in parsed.get('ignore-patterns', []):
            try:
                re.compile(pattern)
            except sre_constants.error:
                add_message(CONFIG_INVALID_REGEXP, 'Invalid regular expression', pattern)

        for key in ProfileValidationTool.LIST_SETTINGS:
            if key not in parsed:
                continue
            if not isinstance(parsed[key], (tuple, list)):
                add_message(CONFIG_SETTING_SHOULD_BE_LIST, '"%s" should be a list' % key, key)

        for key in parsed.keys():
            if key not in ProfileValidationTool.ALL_SETTINGS and key not in self.tool_names():
                add_message(CONFIG_UNKNOWN_SETTING, '"%s" is not a valid prospector setting' % key, key)

        return messages

    def run(self, found_files):
        messages = []
        for filepath in found_files.iter_file_paths(abspath=False, include_ignored=True):
            if filepath in self.to_check:
                messages += self.validate(filepath)
        return messages