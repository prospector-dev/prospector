# -*- coding: utf-8 -*-
import os
import logging
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


PYROMA_CODES = {
    ratings.Name: 'PYR01',
    ratings.Version: 'PYR02',
    ratings.VersionIsString: 'PYR03',
    ratings.PEP386Version: 'PYR04',
    ratings.Description: 'PYR05',
    ratings.LongDescription: 'PYR06',
    ratings.Classifiers: 'PYR07',
    ratings.PythonVersion: 'PYR08',
    ratings.Keywords: 'PYR09',
    ratings.Author: 'PYR10',
    ratings.AuthorEmail: 'PYR11',
    ratings.Url: 'PYR12',
    ratings.License: 'PYR13',
    ratings.ZipSafe: 'PYR14',
    ratings.TestSuite: 'PYR15',
    ratings.SDist: 'PYR16',
    ratings.PackageDocs: 'PYR17',
    ratings.ValidREST: 'PYR18',
    ratings.BusFactor: 'PYR19',
}


PYROMA_TEST_CLASSES = [t.__class__ for t in ratings.ALL_TESTS]


class PyromaTool(ToolBase):

    def __init__(self, *args, **kwargs):
        super(PyromaTool, self).__init__(*args, **kwargs)
        self.ignore_codes = ()

    def configure(self, prospector_config, found_files):
        self.ignore_codes = prospector_config.get_disabled_messages('pyroma')

    def run(self, found_files):
        messages = []
        for module in found_files.iter_module_paths(include_ignored=True):
            dirname, filename = os.path.split(module)
            if filename != 'setup.py':
                continue

            data = projectdata.get_data(dirname)

            all_tests = [m() for m in PYROMA_TEST_CLASSES]
            for test in all_tests:
                code = PYROMA_CODES[test.__class__]

                if code in self.ignore_codes:
                    continue

                passed = test.test(data)
                if passed is False:  # passed can be True, False or None...
                    loc = Location(module, 'setup', None, -1, -1)
                    msg = Message('pyroma', code, loc, test.message())
                    messages.append(msg)

        return messages
