# -*- coding: utf-8 -*-
# pylint: skip-file
import codecs
import os
import sys
from distutils.core import setup

from setuptools import find_packages

with open('prospector/__pkginfo__.py') as f:
    exec(f.read())
_VERSION = globals()['__version__']

if sys.version_info < (2, 7):
    raise Exception('Prospector %s requires Python 2.7 or higher.' % _VERSION)


_PACKAGES = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_INSTALL_REQUIRES = [
    'pylint>=1.5',
    'pylint-celery>=0.3',
    'pylint-django>=0.7',
    'pylint-flask>=0.1',
    'pylint-plugin-utils>=0.2.3',
    'pylint-common>=0.2.2',
    'requirements-detector>=0.4.1',
    'setoptconf>=0.2.0',
    'dodgy>=0.1.9',
    'pyyaml',
    'mccabe>=0.2.1',
    'pyflakes>=0.8.1',
    'pep8>=1.6.0',
    'pep8-naming>=0.2.2',
    'pep257>=0.3.2',
]

_PACKAGE_DATA = {
    'prospector': [
        'blender_combinations.yaml',
        'profiles/profiles/default.yaml',
        'profiles/profiles/doc_warnings.yaml',
        'profiles/profiles/full_pep8.yaml',
        'profiles/profiles/flake8.yaml',
        'profiles/profiles/member_warnings.yaml',
        'profiles/profiles/no_doc_warnings.yaml',
        'profiles/profiles/no_member_warnings.yaml',
        'profiles/profiles/no_pep8.yaml',
        'profiles/profiles/no_test_warnings.yaml',
        'profiles/profiles/strictness_high.yaml',
        'profiles/profiles/strictness_low.yaml',
        'profiles/profiles/strictness_medium.yaml',
        'profiles/profiles/strictness_none.yaml',
        'profiles/profiles/strictness_veryhigh.yaml',
        'profiles/profiles/strictness_verylow.yaml',
    ]
}

_CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Operating System :: Unix',
    'Topic :: Software Development :: Quality Assurance',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: '
    'GNU General Public License v2 or later (GPLv2+)',
)

_OPTIONAL = {
    'with_frosted': ('frosted>=1.4.1',),
    'with_vulture': ('vulture>=0.6',),
    'with_pyroma': ('pyroma>=1.6,<2.0',),
    'with_pep257': (),  # note: this is no longer optional, so this option will be removed in a future release
}
_OPTIONAL['with_everything'] = [req for req_list in _OPTIONAL.values() for req in req_list]


if os.path.exists('README.rst'):
    _LONG_DESCRIPTION = codecs.open('README.rst', 'r', 'utf-8').read()
else:
    _LONG_DESCRIPTION = 'Prospector: python static analysis tool. See http://prospector.landscape.io'


setup(
    name='prospector',
    version=_VERSION,
    url='http://prospector.landscape.io',
    author='landscape.io',
    author_email='code@landscape.io',
    license='GPLv2',
    zip_safe=False,
    description='Prospector: python static analysis tool',
    long_description=_LONG_DESCRIPTION,
    keywords='pylint pyflakes pep8 mccabe frosted prospector static code analysis',
    classifiers=_CLASSIFIERS,
    package_data=_PACKAGE_DATA,
    include_package_data=True,
    packages=_PACKAGES,
    entry_points={
        'console_scripts': [
            'prospector = prospector.run:main',
        ],
    },
    install_requires=_INSTALL_REQUIRES,
    extras_require=_OPTIONAL,
)
