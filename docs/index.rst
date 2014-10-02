.. Prospector documentation master file, created by
   sphinx-quickstart on Sun Sep 28 11:26:59 2014.

Prospector - Python Static Analysis
===================================

.. image:: https://pypip.in/v/prospector/badge.png
   :target: https://pypi.python.org/pypi/prospector
   :alt: Latest Version of Prospector
.. image:: https://travis-ci.org/landscapeio/prospector.png?branch=master
   :target: https://travis-ci.org/landscapeio/prospector
   :alt: Build Status
.. image:: https://landscape.io/github/landscapeio/prospector/master/landscape.png
   :target: https://landscape.io/github/landscapeio/prospector/master
   :alt: Code Health
.. image:: https://coveralls.io/repos/landscapeio/prospector/badge.png
   :target: https://coveralls.io/r/landscapeio/prospector
   :alt: Text Coverage

About
-----

Prospector is a tool to analyse Python code and output information about errors, potential problems, convention violations and complexity.

It brings together the functionality of other Python analysis tools such as `Pylint`_, `pep8`_, and `McCabe complexity`_ . See the 'Supported Tools' section below for a complete list.

The primary aim of Prospector is to be useful 'out of the box'. A common complaint of other Python analysis tools is that it takes a long time to filter through which errors are relevant or interesting to your own coding style. Prospector provides some default profiles, which hopefully will provide a good starting point and be useful straight away. 

Installation
------------

You can install using ``pip``::

    pip install prospector

To install optional dependencies such as ``pyroma``:

    pip install prospector[with_pyroma]

For a full list of optional extras, see the :doc:`section on supported tools </supported_tools>`.

Usage
-----

Simply run prospector from the root of your project::

    prospector


This will output a list of messages pointing out potential problems or errors, for example::

    prospector.tools.base (prospector/tools/base.py):
        L5:0 ToolBase: pylint - R0922
        Abstract class is only referenced 1 times



License
-------

Prospector is available under the GPLv2 License.


Appendix
--------

Supported Tools
```````````````

Currently, prospector runs the following tools:

- `Pylint`_
- `Mccabe complexity`_
- `pyflakes`_
- `pep8`_
- `dodgy`_
- `frosted`_


Supported frameworks and libraries
``````````````````````````````````

Prospector has support for the following frameworks:

- `Celery`_
- `Django`_

If you have a suggestion for another framework or library which should be supported, please `add an issue`_.


Contents:

.. toctree::
   :maxdepth: 1

   features
   usage
   strictness
   profiles
   supported_tools



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _detecting dependencies: https://github.com/landscapeio/requirements-detector
.. _Pylint: http://docs.pylint.org/
.. _McCabe complexity: https://pypi.python.org/pypi/mccabe
.. _pyflakes: https://launchpad.net/pyflakes
.. _pep8: http://pep8.readthedocs.org/en/latest/) (with [pep8-naming](https://github.com/flintwork/pep8-naming)
.. _dodgy: https://github.com/landscapeio/dodgy
.. _frosted: https://github.com/timothycrosley/frosted
.. _Celery: https://github.com/landscapeio/pylint-celery
.. _Django: https://github.com/landscapeio/pylint-django
.. _add an issue: https://github.com/landscapeio/prospector/issues
