import datetime

import pytest

from prospector.formatters import FORMATTERS
from prospector.profiles.profile import ProspectorProfile


@pytest.fixture
def _simple_profile() -> ProspectorProfile:
    return ProspectorProfile(name="horse", profile_dict={}, inherit_order=["horse"])


def test_formatter_types(_simple_profile):
    summary = {
        "started": datetime.datetime(2014, 1, 1),
        "completed": datetime.datetime(2014, 1, 1),
        "message_count": 0,
        "time_taken": "0",
        "libraries": [],
        "strictness": "veryhigh",
        "profiles": "",
        "tools": [],
    }
    for formatter_name, formatter in FORMATTERS.items():
        formatter_instance = formatter(summary, [], _simple_profile)
        assert isinstance(formatter_instance.render(True, True, False), str)
