from collections import defaultdict

from prospector.formatters.text import TextFormatter


__all__ = (
    'GroupedFormatter',
)


class GroupedFormatter(TextFormatter):
    def render_messages(self):
        output = [
            'Messages',
            '========',
            '',
        ]

        # pylint: disable=unnecessary-lambda
        groups = defaultdict(lambda: defaultdict(list))

        for message in self.messages:
            groups[message.location.path][message.location.line].append(message)

        for filename in sorted(groups.keys()):
            output.append(filename)

            for line in sorted(groups[filename].keys(), key=lambda x: 0 if x is None else int(x)):
                output.append('  Line: %s' % line)

                for message in groups[filename][line]:
                    output.append(
                        '    %s: %s / %s%s' % (
                            message.source,
                            message.code,
                            message.message,
                            (' (col %s)' % message.location.character) if message.location.character else '',
                        )
                    )

            output.append('')

        return '\n'.join(output)
