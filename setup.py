# -*- coding: UTF-8 -*-
from distutils.core import setup
from setuptools import find_packages
import time
from prospector import __pkginfo__

_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_short_description = "Prospector: python static analysis tool"

_install_requires = [
    'pylint>=1.0.0',
    'pylint-celery>=0.1',
    'pylint-django>=0.1',
    'pylint-plugin-utils>=0.1',
    'pylint-common>=0.1',
    'requirements-detector>=0.1.1',
    'argparse==1.2.1',
    'pyyaml',
    'pyflakes',
]

_package_data = {
    'prospector': [
        'profiles/profiles/no_doc_warnings.yaml',
        'profiles/profiles/no_test_warnings.yaml',
        'profiles/profiles/strictness_high.yaml',
        'profiles/profiles/strictness_low.yaml',
        'profiles/profiles/strictness_medium.yaml',
        'profiles/profiles/strictness_veryhigh.yaml',
        'profiles/profiles/strictness_verylow.yaml',
    ]
}

_classifiers = (
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: Unix',
    'Topic :: Software Development :: Quality Assurance',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
)

setup(
    name='prospector',
    url='https://github.com/landscapeio/prospector',
    author='landscape.io',
    author_email='code@landscape.io',
    description=_short_description,
    install_requires=_install_requires,
    package_data=_package_data,
    scripts=['bin/prospector'],
    version=__pkginfo__.get_version(),
    packages=_packages,
    license='GPLv2',
    keywords='pylint pyflakes prospector code analysis',
    classifiers=_classifiers
)
