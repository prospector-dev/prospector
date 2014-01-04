import sys

from collections import defaultdict

from .text import _SUMMARY_TEMPLATE


__all__ = (
    'format_messages',
)


def format_messages(summary, messages):
    if summary:
        sys.stdout.write("Check Information\n=================\n")
        sys.stdout.write(_SUMMARY_TEMPLATE % summary)
        sys.stdout.write('\n\n')

    if not messages:
        return

    # pylint: disable=W0108
    groups = defaultdict(lambda: defaultdict(list))

    for message in messages:
        groups[message.location.path][message.location.line].append(message)

    sys.stdout.write("Messages\n========\n\n")
    for filename in sorted(groups.keys()):
        sys.stdout.write('%s\n' % filename)

        for line in sorted(groups[filename].keys(), key=lambda x: 0 if x is None else int(x)):
            sys.stdout.write('  Line: %s\n' % line)

            for msg in groups[filename][line]:
                sys.stdout.write(
                    '    %(source)s: %(code)s / %(message)s' % msg.as_dict(),
                )
                if msg.location.character:
                    sys.stdout.write(' (col %s)' % msg.location.character)
                sys.stdout.write('\n')

        sys.stdout.write('\n')
