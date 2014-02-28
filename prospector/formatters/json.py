from __future__ import absolute_import
from datetime import datetime
import json
import sys


def format_messages(summary, messages, indent=2):
    output = {}

    if summary is not None:
        # we need to slightly change the types and format
        # of a few of the items in the summary to make
        # them play nice with JSON formatting
        munged = {}
        for key, value in summary.iteritems():
            if isinstance(value, datetime):
                munged[key] = str(value)
            else:
                munged[key] = value
        output['summary'] = munged

    if messages is not None:
        output['messages'] = [m.as_dict() for m in messages]

    output = json.dumps(output, indent=indent)
    sys.stdout.write(output + '\n')
