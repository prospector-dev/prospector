# -*- coding: utf-8 -*-
import datetime
from unittest import TestCase

import six
from prospector.formatters import FORMATTERS
from prospector.profiles.profile import ProspectorProfile


class FormatterTypeTest(TestCase):
    def test_formatter_types(self):
        summary = {'started': datetime.datetime(2014, 1, 1),
                   'completed': datetime.datetime(2014, 1, 1),
                   'message_count': 0,
                   'time_taken': '0',
                   'libraries': [],
                   'strictness': 'veryhigh',
                   'profiles': '',
                   'tools': []}
        profile = ProspectorProfile(name='horse',
                                    profile_dict={},
                                    inherit_order=['horse'])
        for formatter_name, formatter in FORMATTERS.items():
            formatter_instance = formatter(summary, [], profile)
            self.assertIsInstance(formatter_instance.render(True, True, False),
                                  six.string_types)
