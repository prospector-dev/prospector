# -*- coding: UTF-8 -*-
from distutils.core import setup
from setuptools import find_packages
from prospector import __pkginfo__


_PACKAGES = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_INSTALL_REQUIRES = [
    'pylint>=1.1.0',
    'pylint-celery>=0.1',
    'pylint-django>=0.3',
    'pylint-plugin-utils>=0.1.1',
    'pylint-common>=0.1',
    'requirements-detector>=0.1.2',
    'setoptconf>=0.2.0',
    'dodgy>=0.1.5',
    'pyyaml',
    'mccabe>=0.2.1',
    'pyflakes>=0.8',
    'pep8>=1.4.2',
    'pep8-naming>=0.2.1',
    'frosted>=1.4.0',
]

_PACKAGE_DATA = {
    'prospector': [
        'blender_combinations.yaml',
        'profiles/profiles/full_pep8.yaml',
        'profiles/profiles/no_doc_warnings.yaml',
        'profiles/profiles/no_pep8.yaml',
        'profiles/profiles/no_test_warnings.yaml',
        'profiles/profiles/strictness_high.yaml',
        'profiles/profiles/strictness_low.yaml',
        'profiles/profiles/strictness_medium.yaml',
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
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'License :: OSI Approved :: '
    'GNU General Public License v2 or later (GPLv2+)',
)


setup(
    name='prospector',
    version=__pkginfo__.get_version(),
    url='https://github.com/landscapeio/prospector',
    author='landscape.io',
    author_email='code@landscape.io',
    license='GPLv2',
    description='Prospector: python static analysis tool',
    keywords='pylint pyflakes pep8 mccabe frosted prospector code analysis',
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
)
