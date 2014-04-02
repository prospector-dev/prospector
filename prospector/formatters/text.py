from prospector.formatters.base import Formatter


__all__ = (
    'TextFormatter',
)


# pylint: disable=W0108


class TextFormatter(Formatter):
    summary_labels = (
        ('started', 'Started'),
        ('completed', 'Finished'),
        ('time_taken', 'Time Taken', lambda x: '%s seconds' % x),
        ('formatter', 'Formatter'),
        ('strictness', 'Strictness'),
        ('libraries', 'Libraries Used', lambda x: ', '.join(x)),
        ('tools', 'Tools Run', lambda x: ', '.join(x)),
        ('adaptors', 'Adaptors', lambda x: ', '.join(x)),
        ('message_count', 'Message Found'),
    )

    def render_summary(self):
        output = [
            'Check Information',
            '=================',
        ]

        label_width = max([len(label[1]) for label in self.summary_labels])

        for summary_label in self.summary_labels:
            key = summary_label[0]
            if key in self.summary:
                label = summary_label[1]
                if len(summary_label) > 2:
                    value = summary_label[2](self.summary[key])
                else:
                    value = self.summary[key]
                output.append(
                    '%s: %s' % (
                        label.rjust(label_width),
                        value,
                    )
                )

        return '\n'.join(output)

    # pylint: disable=R0201
    def render_message(self, message):
        output = []

        if message.location.module:
            output.append('%s (%s):' % (
                message.location.module,
                message.location.path
            ))
        else:
            output.append('%s:' % message.location.path)

        output.append(
            '    L%s:%s %s: %s - %s' % (
                message.location.line or '-',
                message.location.character if message.location.line else '-',
                message.location.function,
                message.source,
                message.code,
            )
        )

        output.append('    %s' % message.message)

        return '\n'.join(output)

    def render_messages(self):
        output = [
            'Messages',
            '========',
            '',
        ]

        for message in self.messages:
            output.append(self.render_message(message))
            output.append('')

        return '\n'.join(output)

    def render(self, summary=True, messages=True):
        output = ''
        if summary:
            output = self.render_summary()
        output += '\n\n\n'
        if messages:
            output += self.render_messages()
        return output.strip()
