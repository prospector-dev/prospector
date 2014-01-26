from __future__ import absolute_import
import json
import sys


def format_messages(summary, messages, indent=2):
    output = {}

    if summary is not None:
        output['summary'] = summary

    if messages is not None:
        output['messages'] = [m.as_dict() for m in messages]

    output = json.dumps(output, indent=indent)
    sys.stdout.write(output + '\n')
