# coding: utf8
import os
import sys
import codecs
import warnings
import tempfile
import contextlib
from unittest import TestCase
try:
    from unittest.util import safe_repr
except ImportError:
    # python2.6
    safe_repr = repr

from prospector.autodetect import (
    autodetect_libraries,
    find_from_imports,
    find_from_path,
)

class FindFromImportsTest(TestCase):

    def _test(self, contents, *expected_names):
        names = find_from_imports(contents)
        self.assertEqual(set(expected_names), names)

    def test_simple_imports(self):
        """ imports related to django are discovered. """
        self._test('from django.db import models', 'django')
        self._test('import django', 'django')

    def test_compound_discovered(self):
        """ compound imports containing several items of interest are discovered. """
        self._test('from django import db\nfrom celery import task', 'django', 'celery')

    def test_nothing_of_interest(self):
        """ imports containing nothing of interest return an empty set. """
        self._test('import codecs')

    def test_multiple_imports(self):
        """ django is discovered in 'from ...' multi-import statements. """
        self._test('from django.db import (models, \n'
                   '    some, other, stuff)', 'django')

    def test_indented_imports(self):
        """ django is discovered from function-local import statements. """
        self._test('def lala(self):\n'
                   'from django.db import models\n'
                   'return models.Model', 'django')

    def test_same_line_two_imports(self):
        """ importing two modules of interest on same line are discovered. """
        self._test('import django, celery', 'django', 'celery')


class ImportCodingsTest(TestCase):

    def SetUp(self):
        warnings.simplefilter(action='always', category=ImportWarning)
        TestCase.setUp(self)

    def tearDown(self):
        warnings.resetwarnings()
        TestCase.tearDown(self)

    if sys.version_info < (2, 7):
        # backport assertGreaterEqual and assertIn for python2.6.

        def assertGreaterEqual(self, a, b, msg=None):
            """Just like self.assertTrue(a >= b), but with a nicer default message."""
            if not a >= b:
                standardMsg = '%s not greater than or equal to %s' % (safe_repr(a), safe_repr(b))
                self.fail(self._formatMessage(msg, standardMsg))

        def assertIn(self, member, container, msg=None):
            """Just like self.assertTrue(a in b), but with a nicer default message."""
            if member not in container:
                standardMsg = '%s not found in %s' % (safe_repr(member),
                                                      safe_repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

    @contextlib.contextmanager
    def make_pypath(self, bindata):
        tmp_folder = tempfile.mkdtemp(prefix='prospector-')
        tmp_fp = tempfile.NamedTemporaryFile(suffix='.py', dir=tmp_folder, delete=False)
        tmp_file = tmp_fp.name
        tmp_fp.write(bindata)
        tmp_fp.close()
        try:
            yield tmp_folder
        finally:
            os.unlink(tmp_file)
            os.rmdir(tmp_folder)

    def test_latin1_coding_line2(self):
        """
        File containing latin1 at line 2 with 'coding' declaration at line 1.
        """
        # given,
        bindata = (u'# coding: latin1\n'
                   u'# latin1 character: ®\n'
                   u'import django\n'
                   ).encode('latin1')
        expected_names = ('django',)
        with self.make_pypath(bindata=bindata) as path:
            # exercise,
            names = find_from_path(path=path)
        # verify.
        self.assertEqual(set(expected_names), names)

    def test_negative_latin1(self):
        """ Negative test: file containing latin1 without 'coding' declaration. """
        # given,
        bindata = u'# latin1 character: ®'.encode('latin1')

        with self.make_pypath(bindata=bindata) as path:
            # exercise,
            with warnings.catch_warnings(record=True) as warned:
                find_from_path(path=path)
                # verify.
                self.assertGreaterEqual(len(warned), 1)
                self.assertIn(ImportWarning, [_w.category for _w in warned])

    def test_negative_lookuperror(self):
        """ File declares an unknown coding.  """
        # given,
        bindata = u'# coding: unknown\n'.encode('ascii')

        with self.make_pypath(bindata=bindata) as path:
            # exercise,
            with warnings.catch_warnings(record=True) as warned:
                find_from_path(path=path)
                # verify.
                self.assertGreaterEqual(len(warned), 1)
                self.assertIn(ImportWarning, [_w.category for _w in warned])

    def test_bom_encoded_filepath(self):
        """ File containing only a UTF32_BE byte order mark still decodes.  """
        # given,
        bindata = codecs.BOM_UTF32_BE
        bindata += (u'import django\n'
                    u'# UTF-32-BE character: ®\n'
                    ).encode('UTF-32BE')
        expected_names = ('django',)
        with self.make_pypath(bindata=bindata) as path:
            # exercise,
            names = find_from_path(path=path)
        # verify.
        self.assertEqual(set(expected_names), names)

    def test_negative_misleading_bom(self):
        """ Negative test: file containing BOM that is not the correct encoding. """
        # given,
        bindata = codecs.BOM_UTF32_BE
        bindata += u'# latin1 character: ®'.encode('latin1')

        with self.make_pypath(bindata=bindata) as path:
            # exercise,
            with warnings.catch_warnings(record=True) as warned:
                find_from_path(path=path)
                # verify.
                self.assertGreaterEqual(len(warned), 1)
                self.assertIn(ImportWarning, [_w.category for _w in warned])


class AdaptersTest(TestCase):

    """ Adapters detection requires a true project, we just use only our own. """

    def test_autodetect_adapters_of_prospector(self):
        """ Use prospector's base proj. folder, discovers nothing. """
        # Given
        tgt_path = os.path.join(os.path.dirname(__file__), os.path.pardir)

        # Exercise
        detected = autodetect_libraries(tgt_path)

        # Verify
        self.assertEqual(set(), detected)


if __name__ == '__main__':
    import unittest
    unittest.main()
