# -*- coding: utf-8 -*-
from __future__ import absolute_import

from mypy import api

from prospector.message import Location, Message
from prospector.tools import ToolBase


__all__ = (
    'MypyTool',
)


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
        python_2_mode = options.get('python-2-mode', False)
        strict_optional = options.get('strict-optional', False)

        allowed_options = options.get('allow', [])
        check_options = options.get('check', [])
        disallowed_options = options.get('disallow', [])
        no_check_options = options.get('no-check', [])
        no_warn_options = options.get('no-warn', [])
        warn_options = options.get('warn', [])

        self.options.append('--follow-imports=%s' % follow_imports)

        if ignore_missing_imports:
            self.options.append('--ignore-missing-imports')

        if implict_optional:
            self.options.append('--implict-optional')

        if python_2_mode:
            self.options.append('--py2')

        if strict_optional:
            self.options.append('--strict-optional')

        for entry in allowed_options:
            self.options.append('--allow-%s' % entry)
        
        for entry in check_options:
            self.options.append('--check-%s' % entry)

        for entry in disallowed_options:
            self.options.append('--disallow-%s' % entry)

        for entry in no_check_options:
            self.options.append('--no-check-%s' % entry)

        for entry in no_warn_options:
            self.options.append('--no-warn-%s' % entry)

        for entry in warn_options:
            self.options.append('--warn-%s' % entry)

    def run(self, found_files):
        paths = [path for path in found_files.iter_module_paths()]
        paths.extend(self.options)
        report, *_ = self.checker.run(paths)
        messages = []

        for message in report.splitlines():
            path, line, char, err_type, *err_msg = message.split(':')
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