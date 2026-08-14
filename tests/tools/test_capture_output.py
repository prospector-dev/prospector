import io
import sys

from prospector.tools.utils import CaptureOutput


def test_captured_stdout_is_an_initialised_text_stream() -> None:
    """
    While output is captured, ``sys.stdout`` must still behave like a text stream.

    Prospector replaces ``sys.stdout``/``sys.__stdout__`` for the whole duration of a
    tool run, so any code touching the standard stream (a pylint plugin, Django, a
    progress bar...) talks to ``CaptureStream`` instead of the real one.
    """
    with CaptureOutput(hide=True) as capture:
        stream = sys.stdout
        encoding = stream.encoding
        errors = stream.errors
        writable = stream.writable()
        readable = stream.readable()
        print("hello")

    assert capture.get_hidden_stdout() == "hello\n"
    assert isinstance(encoding, str)
    assert encoding != ""
    assert isinstance(errors, str)
    assert errors != ""
    assert writable is True
    assert readable is False


def test_captured_stdout_fileno_raises_unsupported_operation() -> None:
    """
    ``fileno()`` has no file descriptor to return, but it must fail the way other
    in-memory streams do (like ``io.StringIO``), not with "uninitialized object"."""
    raised: BaseException
    with CaptureOutput(hide=True):
        stream = sys.stdout
        try:
            stream.fileno()
        except BaseException as err:  # noqa: BLE001 - the exception type is what we assert on
            raised = err
        else:
            raised = AssertionError("fileno() did not raise")

    assert isinstance(raised, io.UnsupportedOperation), repr(raised)
