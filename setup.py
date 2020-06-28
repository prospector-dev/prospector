# -*- coding: utf-8 -*-
# pylint: skip-file
import codecs
import os
import sys
from distutils.core import setup

from setuptools import find_packages

with open("prospector/__pkginfo__.py") as f:
    exec(f.read())
_VERSION = globals()["__version__"]

if sys.version_info < (3, 5):
    raise Exception("Prospector %s requires Python 3.5 or higher." % _VERSION)


_PACKAGES = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_INSTALL_REQUIRES = [
    "pylint-plugin-utils>=0.2.6",
    "pylint-celery==0.3",
    "pylint-flask==0.6",
    "requirements-detector>=0.6",
    "setoptconf>=0.2.0",
    "dodgy>=0.1.9",
    "pyyaml",
    "mccabe>=0.5.0",
    "pyflakes<2.3.0,>=2.2.0",
    "pycodestyle<2.7.0,>=2.6.0",
    "pep8-naming>=0.3.3,<=0.10.0",
    "pydocstyle>=2.0.0",
    "pylint==2.5.2",
    "pylint-django==2.0.15",
    "astroid==2.4.1",
]


_PACKAGE_DATA = {"prospector": ["blender_combinations.yaml",]}
profiledir = os.path.join(os.path.dirname(__file__), "prospector/profiles/profiles")
_PACKAGE_DATA["prospector"] += [profile for profile in os.listdir(profiledir)]

_CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: Unix",
    "Topic :: Software Development :: Quality Assurance",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: " "GNU General Public License v2 or later (GPLv2+)",
]

_OPTIONAL = {
    "with_bandit": ("bandit>=1.5.1",),
    "with_frosted": ("frosted>=1.4.1",),
    "with_vulture": ("vulture>=1.5",),
    "with_pyroma": ("pyroma>=2.4",),
    "with_mypy": ("mypy>=0.600",),
}

with_everything = [req for req_list in _OPTIONAL.values() for req in req_list]
_OPTIONAL["with_everything"] = sorted(with_everything)

if os.path.exists("README.rst"):
    _LONG_DESCRIPTION = codecs.open("README.rst", "r", "utf-8").read()
else:
    _LONG_DESCRIPTION = "Prospector: python static analysis tool. See http://prospector.readthedocs.io"


setup(
    name="prospector",
    version=_VERSION,
    url="http://prospector.readthedocs.io",
    author="landscape.io",
    author_email="code@landscape.io",
    maintainer="Carlos Coelho",
    maintainer_email="carlospecter@gmail.com",
    license="GPLv2",
    zip_safe=False,
    description="Prospector: python static analysis tool",
    long_description=_LONG_DESCRIPTION,
    keywords="pylint pyflakes pep8 mccabe frosted prospector static code analysis",
    classifiers=_CLASSIFIERS,
    package_data=_PACKAGE_DATA,
    include_package_data=True,
    packages=_PACKAGES,
    entry_points={"console_scripts": ["prospector = prospector.run:main",]},
    install_requires=_INSTALL_REQUIRES,
    extras_require=_OPTIONAL,
)
