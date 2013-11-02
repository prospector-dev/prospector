# -*- coding: UTF-8 -*-
from distutils.core import setup
from setuptools import find_packages
import time


_version = "0.2.dev%s" % int(time.time())
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_short_description = "prospector"

_install_requires = [
    'pylint>=1.0.0',
    'pylint-celery>=0.1',
    'pylint-django>=0.1',
    'pylint-plugin-utils>=0.1',
    'pylint-common>=0.1',
    'requirements-detector>=0.1',
    'argparse==1.2.1',
    'pyyaml',
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

setup(
    name='prospector',
    url='https://github.com/landscapeio/prospector',
    author='landscape.io',
    author_email='code@landscape.io',
    description=_short_description,
    install_requires=_install_requires,
    package_data=_package_data,
    scripts=['bin/prospector'],
    version=_version,
    packages=_packages,
    license='GPLv2',
    keywords='pylint prospector code analysis'
)
