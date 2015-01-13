from __future__ import absolute_import

import json

from datetime import datetime

from prospector.formatters.base import Formatter


__all__ = (
    'JsonFormatter',
)


# pylint: disable=too-few-public-methods
class JsonFormatter(Formatter):
    def render(self, summary=True, messages=True, profile=False):
        output = {}

        if summary:
            # we need to slightly change the types and format
            # of a few of the items in the summary to make
            # them play nice with JSON formatting
            munged = {}
            for key, value in self.summary.items():
                if isinstance(value, datetime):
                    munged[key] = str(value)
                else:
                    munged[key] = value
            output['summary'] = munged

        if profile:
            output['profile'] = self.profile.as_dict()

        if messages:
            output['messages'] = [m.as_dict() for m in self.messages]

        return json.dumps(output, indent=2)
