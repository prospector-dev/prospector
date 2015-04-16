from __future__ import absolute_import

import yaml

from prospector.formatters.base import Formatter


__all__ = (
    'YamlFormatter',
)


# pylint: disable=too-few-public-methods
class YamlFormatter(Formatter):
    def render(self, summary=True, messages=True, profile=False):
        output = {}

        if summary:
            output['summary'] = self.summary

        if profile:
            output['profile'] = self.profile.as_dict()

        if messages:
            output['messages'] = [m.as_dict() for m in self.messages]

        return yaml.safe_dump(
            output,
            indent=2,
            default_flow_style=False,
            allow_unicode=True,
        )
