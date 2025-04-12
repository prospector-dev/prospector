from pathlib import Path

import pytest

from prospector.pathutils import is_python_module


@pytest.mark.parametrize(  # type: ignore[misc]
    ("filename", "expected"),
    [
        ("file.py", True),
        ("file.txt", False),
        ("scrypt1", False),
        ("scrypt2", False),
        ("scrypt_py1", True),
        ("scrypt_py2", True),
        ("scrypt_py3", True),
        ("scrypt_py4", True),
        ("no_exec", False),
    ],
)
def test_is_python_module(filename: str, expected: bool) -> None:
    path = Path(__file__).parent / filename
    assert is_python_module(path) == expected
