import logging
import os

from prospector.message import Location, Message
from prospector.tools.base import ToolBase

# HACK: pyroma configures logging in its __init__.py so by importing,
# it will change existing logging configuration to DEBUG which causes
# problems with other 3rd party modules as everything now logs to
# stdout...
_old = logging.basicConfig
try:
    logging.basicConfig = lambda **k: None
    from pyroma import projectdata, ratings
except ImportError:
    # raise the Exception
    raise
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
for name, code in PYROMA_ALL_CODES.items():
    if hasattr(ratings, name):
        PYROMA_CODES[getattr(ratings, name)] = code

PYROMA_TEST_CLASSES = [t.__class__ for t in ratings.ALL_TESTS]


class PyromaTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(PyromaTool, self).__init__(*args, **kwargs)
        self.ignore_codes = ()

    def configure(self, prospector_config, found_files):
        self.ignore_codes = prospector_config.get_disabled_messages("pyroma")

    def run(self, found_files):
        messages = []
        for module in found_files.iter_module_paths(include_ignored=True):
            dirname, filename = os.path.split(module)
            if filename != "setup.py":
                continue

            data = projectdata.get_data(dirname)

            all_tests = [m() for m in PYROMA_TEST_CLASSES]
            for test in all_tests:
                code = PYROMA_CODES.get(test.__class__, "PYRUNKNOWN")

                if code in self.ignore_codes:
                    continue

                passed = test.test(data)
                if passed is False:  # passed can be True, False or None...
                    loc = Location(module, "setup", None, -1, -1)
                    msg = Message("pyroma", code, loc, test.message())
                    messages.append(msg)

        return messages
