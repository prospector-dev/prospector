# this one is not ignored and should still be picked up
from distutils.core import setup
from setuptools import find_packages

_version = "1.0.1.1.0.0.1.1.0"
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "example"])


_classifiers = (
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7',
)

setup(
    name='testing-pkg',
    author='Winston Flarp-le-garde',
    author_email='testing@example.com',
    version=_version,
    packages=_packages,
    license='BSD',
    classifiers=_classifiers
)