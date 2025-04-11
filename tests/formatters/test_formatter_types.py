import datetime
from pathlib import Path
from typing import Any

import pytest

from prospector.formatters import FORMATTERS
from prospector.message import Location, Message
from prospector.profiles.profile import ProspectorProfile


@pytest.fixture  # type: ignore[misc]
def _simple_profile() -> ProspectorProfile:
    return ProspectorProfile(name="horse", profile_dict={}, inherit_order=["horse"])


@pytest.fixture  # type: ignore[misc]
def _simple_summary() -> dict[str, Any]:
    return {
        "started": datetime.datetime(2014, 1, 1),
        "completed": datetime.datetime(2014, 1, 1),
        "message_count": 0,
        "time_taken": "0",
        "libraries": [],
        "strictness": "veryhigh",
        "profiles": "",
        "tools": [],
    }


def test_formatter_types(_simple_summary: Any, _simple_profile: Any) -> None:
    for formatter in FORMATTERS.values():
        formatter_instance = formatter(_simple_summary, [], _simple_profile)
        assert isinstance(formatter_instance.render(True, True, False), str)


def test_formatters_render(_simple_summary: Any, _simple_profile: Any) -> None:
    """
    Basic test to ensure that formatters can at least render messages without erroring
    """
    for formatter in FORMATTERS.values():
        messages = [
            Message(
                "testtool",
                "oh-no",
                Location(Path(__file__), "formatters/test_formatter_types", "test_formatters_render", 39, 12),
                "testing formatters work",
            )
        ]
        formatter_instance = formatter(_simple_summary, messages, _simple_profile)
        formatter_instance.render(True, True, False)
