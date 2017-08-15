# -*- coding: utf-8 -*-
from itertools import islice
from mypy import api

from prospector.message import Location, Message
from prospector.tools import ToolBase


__all__ = (
    'MypyTool',
)


MYPY_OPTIONS = [
    'allow',
    'check',
    'disallow',
    'no-check',
    'no-warn',
    'warn'
]


class MypyTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(MypyTool, self).__init__(*args, **kwargs)
        self.checker = api
        self.options = ['--show-column-numbers']

    def configure(self, prospector_config, _):
        options = prospector_config.tool_options('mypy')

        follow_imports = options.get('follow-imports', 'normal')
        ignore_missing_imports = options.get('ignore-missing-imports', False)
        implict_optional = options.get('implict-optional', False)
        platform = options.get('platform', None)
        python_2_mode = options.get('python-2-mode', False)
        python_version = options.get('python-version', None)
        strict_optional = options.get('strict-optional', False)

        self.options.append('--follow-imports=%s' % follow_imports)

        if ignore_missing_imports:
            self.options.append('--ignore-missing-imports')

        if implict_optional:
            self.options.append('--implict-optional')

        if platform:
            self.options.append('--platform %s' % platform)

        if python_2_mode:
            self.options.append('--py2')

        if python_version:
            self.options.append('--python-version %s' % python_version)

        if strict_optional:
            self.options.append('--strict-optional')

        for list_option in MYPY_OPTIONS:
            for entry in options.get(list_option, []):
                self.options.append('--%s-%s' % (list_option, entry))

    def run(self, found_files):
        paths = [path for path in found_files.iter_module_paths()]
        paths.extend(self.options)
        result = self.checker.run(paths)
        report, _ = result[0], result[1:]
        messages = []

        for message in report.splitlines():
            iter_message = iter(message.split(':'))
            (path, line, char, err_type), err_msg = islice(iter_message, 4), list(message)
            location = Location(
                path=path,
                module=None,
                function=None,
                line=line,
                character=char,
                absolute_path=True
            )
            message = Message(
                source='mypy',
                code=err_type,
                location=location,
                message=''.join(err_msg).strip()
            )
            messages.append(message)

        return messages