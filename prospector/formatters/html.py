# -*- coding: utf-8 -*-
import os

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from prospector.formatters.base import Formatter

__all__ = (
    'HTMLFormatter',
)


# pylint: disable=unnecessary-lambda


class HTMLFormatter(Formatter):
    TEMPLATE_PATHS = (
        '.',
        os.path.join(os.path.dirname(__file__), 'templates'),
    )

    TEMPLATE = 'formatter.html'

    def render_template(self, **context):
        """
        Render HTML using Jinja2 template.

        :param context: Context to render template.
        :return: Rendered template.
        """
        loader = FileSystemLoader(self.TEMPLATE_PATHS)
        env = Environment(loader=loader)
        return env.get_template(self.TEMPLATE).render(**context)

    def render(self, summary=True, messages=True, profile=False):
        context = {}
        if messages and self.messages:  # if there are no messages, don't render an empty header
            context['messages'] = self.messages
        if profile:
            context['profile'] = self.profile.as_yaml().strip()
        if summary:
            context['summary'] = {k: v for k, v in self.summary.items() if v}

        return self.render_template(**context)
