from unittest import TestCase

from prospector import blender
from prospector.message import Location, Message


class TestBlendLine(TestCase):
    BLEND = [
        [("s1", "s1c01"), ("s2", "s2c12")],
        [("s3", "s3c81"), ("s1", "s1c04"), ("s2", "s2c44")],
    ]

    def _do_test(self, messages: tuple[tuple[str, str], ...], expected: tuple[tuple[str, str], ...]) -> None:
        def _msg(source: str, code: str) -> Message:
            loc = Location("path.py", "path", None, 1, 0)
            return Message(source, code, loc, "Test Message")

        messages_list = [_msg(*m) for m in messages]
        expected_set = set(expected)

        blended = blender.blend_line(messages_list, TestBlendLine.BLEND)
        result = {(msg.source, msg.code) for msg in blended}

        self.assertEqual(expected_set, result)

    def test_blend_line(self) -> None:
        messages = (("s2", "s2c12"), ("s2", "s2c11"), ("s1", "s1c01"))

        expected = (
            ("s1", "s1c01"),
            ("s2", "s2c11"),  # s2c12 should be blended with s1c01
        )
        self._do_test(messages, expected)

    def test_single_blend(self) -> None:
        # these three should be blended together
        messages = (
            ("s1", "s1c04"),
            ("s2", "s2c44"),
            ("s3", "s3c81"),
        )
        # the s3 message is the highest priority
        expected = (("s3", "s3c81"),)
        self._do_test(messages, expected)

    def test_nothing_to_blend(self) -> None:
        """
        Verifies that messages pass through if there is nothing to blend
        """
        messages = (("s4", "s4c99"), ("s4", "s4c01"), ("s5", "s5c51"), ("s6", "s6c66"))
        self._do_test(messages, messages)  # expected = messages

    def test_no_messages(self) -> None:
        """
        Ensures that the blending works fine when there are no messages to blend
        """
        self._do_test((), ())


def test_multiple_lines() -> None:
    def _msg(source: str, code: str, line_number: int) -> Message:
        loc = Location("path.py", "path", None, line_number, 0)
        return Message(source, code, loc, "Test Message")

    messages = [
        _msg("s1", "s1c001", 4),
        _msg("s2", "s2c001", 6),
        _msg("s2", "s2c101", 4),
        _msg("s1", "s1c001", 6),
    ]

    result = blender.blend(messages, [[("s1", "s1c001"), ("s2", "s2c101")]])
    result_tuple = [(msg.source, msg.code, msg.location.line) for msg in result]
    result_set = set(result_tuple)

    expected = {("s1", "s1c001", 4), ("s1", "s1c001", 6), ("s2", "s2c001", 6)}

    assert expected == result_set
