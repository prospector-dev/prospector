import datetime
from pathlib import Path

import pytest

from prospector.formatters import FORMATTERS
from prospector.message import Location, Message
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


def test_formatters_render(_simple_profile):
    """
    Basic test to ensure that formatters can at least render messages without erroring
    """
    for formatter_name, formatter in FORMATTERS.items():
        messages = [
            Message(
                "testtool",
                "oh-no",
                Location(Path(__file__), "formatters/test_formatter_types", "test_formatters_render", 39, 12),
                "testing formatters work",
            )
        ]
        formatter_instance = formatter({}, messages, _simple_profile)
        formatter_instance.render(True, True, False)
