# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from bandit.cli.main import _get_profile, _init_extensions
from bandit.core.config import BanditConfig
from bandit.core.constants import RANKING
from bandit.core.manager import BanditManager

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


class BanditTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(BanditTool, self).__init__(*args, **kwargs)
        self.manager = None
        self.profile = None
        self.config_file = None
        self.agg_type = 'file'
        self.severity = 0
        self.confidence = 0

    def configure(self, prospector_config, _):
        options = prospector_config.tool_options('bandit')

        if 'profile' in options:
            self.profile = options['profile']

        if 'config' in options:
            self.config_file = options['config']

        if 'severity' in options:
            self.severity = options['severity']
            if not 0 <= self.severity <= 2:
                raise ValueError('severity {!r} must be between 0 and 2'.format(self.severity))

        if 'confidence' in options:
            self.confidence = options['confidence']
            if not 0 <= self.confidence <= 2:
                raise ValueError('confidence {!r} must be between 0 and 2'.format(self.confidence))

        b_conf = BanditConfig(config_file=self.config_file)
        profile = _get_profile(b_conf, self.profile, self.config_file)
        extension_mgr = _init_extensions()
        extension_mgr.validate_profile(profile)

        self.manager = BanditManager(b_conf, None, profile=profile)

    def run(self, found_files):
        self.manager.files_list = sorted(found_files.iter_file_paths())
        self.manager.exclude_files = []

        if not self.manager.b_ts.tests:
            raise ValueError('No test will run for bandit')

        self.manager.run_tests()
        results = self.manager.get_issue_list(
            sev_level=RANKING[self.severity],
            conf_level=RANKING[self.confidence]
        )
        messages = []
        for result in results:
            loc = Location(os.path.abspath(result.fname), None, '', int(result.lineno), 0)
            msg = Message('bandit', result.test_id, loc, result.text)
            messages.append(msg)
        return messages
