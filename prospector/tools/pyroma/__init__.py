import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Optional

from prospector.finder import FileFinder
from prospector.message import Location, Message
from prospector.tools.base import ToolBase

if TYPE_CHECKING:
    from prospector.config import ProspectorConfig


# HACK: pyroma configures logging in its __init__.py so by importing,
# it will change existing logging configuration to DEBUG which causes
# problems with other 3rd party modules as everything now logs to
# stdout...
_old = logging.basicConfig
try:
    logging.basicConfig = lambda **k: None
    from pyroma import projectdata, ratings

    # if pyroma doesn't exist, will raise an ImportError and be caught "upstream"
finally:
    # always restore logging.basicConfig
    logging.basicConfig = _old

PYROMA_ALL_CODES = {
    "Name": "PYR01",
    "Version": "PYR02",
    "VersionIsString": "PYR03",
    "PEPVersion": "PYR04",
    "Description": "PYR05",
    "LongDescription": "PYR06",
    "Classifiers": "PYR07",
    "PythonVersion": "PYR08",
    "Keywords": "PYR09",
    "Author": "PYR10",
    "AuthorEmail": "PYR11",
    "Url": "PYR12",
    "License": "PYR13",
    "LicenceClassifier": "PYR14",
    "ZipSafe": "PYR15",
    "SDist": "PYR16",
    "PackageDocs": "PYR17",
    "ValidREST": "PYR18",
    "BusFactor": "PYR19",
}

PYROMA_CODES = {}


def _copy_codes() -> None:
    for name, code in PYROMA_ALL_CODES.items():
        if hasattr(ratings, name):
            PYROMA_CODES[getattr(ratings, name)] = code


_copy_codes()

PYROMA_TEST_CLASSES = [t.__class__ for t in ratings.ALL_TESTS]


class PyromaTool(ToolBase):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.ignore_codes: list[str] = []

    def configure(  # pylint: disable=useless-return
        self, prospector_config: "ProspectorConfig", found_files: FileFinder
    ) -> Optional[tuple[str, Optional[Iterable[Message]]]]:
        self.ignore_codes = prospector_config.get_disabled_messages("pyroma")
        return None

    def run(self, found_files: FileFinder) -> list[Message]:
        messages = []
        for directory in found_files.directories:
            # just list directories which are not ignored, but find any `setup.py` ourselves
            # as that is excluded by default
            for filepath in directory.iterdir():
                if filepath.is_dir() or filepath.name != "setup.py":
                    continue

                data = projectdata.get_data(directory.resolve())

                all_tests = [m() for m in PYROMA_TEST_CLASSES]
                for test in all_tests:
                    code = PYROMA_CODES.get(test.__class__, "PYRUNKNOWN")

                    if code in self.ignore_codes:
                        continue

                    passed = test.test(data)
                    if passed is False:  # passed can be True, False or None...
                        loc = Location(filepath, "setup", None, -1, -1)
                        msg = Message("pyroma", code, loc, test.message())
                        messages.append(msg)

        return messages
