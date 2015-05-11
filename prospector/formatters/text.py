from prospector.formatters.base import Formatter


__all__ = (
    'TextFormatter',
)


# pylint: disable=unnecessary-lambda


class TextFormatter(Formatter):
    summary_labels = (
        ('started', 'Started'),
        ('completed', 'Finished'),
        ('time_taken', 'Time Taken', lambda x: '%s seconds' % x),
        ('formatter', 'Formatter'),
        ('profiles', 'Profiles'),
        ('strictness', 'Strictness'),
        ('libraries', 'Libraries Used', lambda x: ', '.join(x)),
        ('tools', 'Tools Run', lambda x: ', '.join(x)),
        ('adaptors', 'Adaptors', lambda x: ', '.join(x)),
        ('message_count', 'Messages Found'),
        ('external_config', 'External Config'),
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
                    ' %s: %s' % (
                        label.rjust(label_width),
                        value,
                    )
                )

        return '\n'.join(output)

    # pylint: disable=no-self-use
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
                message.location.character if message.location.character else '-',
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

    def render_profile(self):
        output = [
            'Profile',
            '=======',
            '',
            self.profile.as_yaml().strip()
        ]

        return '\n'.join(output)

    def render(self, summary=True, messages=True, profile=False):
        output = []
        if messages and self.messages:  # if there are no messages, don't render an empty header
            output.append(self.render_messages())
        if profile:
            output.append(self.render_profile())
        if summary:
            output.append(self.render_summary())

        return '\n\n\n'.join(output) + '\n'
