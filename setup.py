# -*- coding: UTF-8 -*-
from distutils.core import setup
from setuptools import find_packages
import time


_version = "0.1.dev%s" % int(time.time())
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_short_description = "prospector"

_install_requires = [
    'pylint==1.0.0',
    'pylint-celery',
    'pylint-django',
]

setup(
    name='prospector',
    url='https://github.com/landscapeio/prospector',
    author='landscape.io',
    author_email='code@landscape.io',
    description=_short_description,
    install_requires=_install_requires,
    scripts=['bin/prospector'],
    version=_version,
    packages=_packages,
    license='GPLv2',
    keywords=('pylint', 'prospector', 'code analysis')
)
