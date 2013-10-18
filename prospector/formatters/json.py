from __future__ import absolute_import
import json


def format_messages(messages, indent=2):
    output = {'messages': [m.as_dict() for m in messages]}
    print json.dumps(output, indent=indent)
