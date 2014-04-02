from __future__ import absolute_import

import yaml

from prospector.formatters.base import Formatter


__all__ = (
    'YamlFormatter',
)


# pylint: disable=R0903
class YamlFormatter(Formatter):
    def render(self, summary=True, messages=True):
        output = {}

        if summary:
            output['summary'] = self.summary

        if messages:
            output['messages'] = [m.as_dict() for m in self.messages]

        return yaml.safe_dump(
            output,
            indent=2,
            default_flow_style=False,
            encoding='utf-8',
            allow_unicode=True,
        )
