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

Usage
-----

Simply run prospector from the root of your project::

    prospector


This will output a list of messages pointing out potential problems or errors, for example::

    prospector.tools.base (prospector/tools/base.py):
        L5:0 ToolBase: pylint - R0922
        Abstract class is only referenced 1 times


Options
```````

Run ``prospector --help`` for a full list of options and their effects.

Output Format
'''''''''''''

The default output format of ``prospector`` is designed to be human readable. For parsing (for example, for reporting), you can use the ``--output-format json`` flag to get JSON-formatted output.

If your code uses frameworks and libraries
''''''''''''''''''''''''''''''''''''''''''

Often tools such as pylint find errors in code which is not an error, due to, for example, attributes of classes being created at run time by a library or framework used by your project. For example, by default, pylint will generate an error for Django models when accessing ``objects``, as the ``objects`` attribute is not part of the ``Model`` class definition. 

Prospector mitigates this by providing an understanding of these frameworks to the underlying tools.

Prospector will try to intuit which libraries your project uses by `detecting dependencies`_ and automatically turning on support for the requisite libraries. You can see which adaptors were run in the metadata section of the report.

If Prospector does not correctly detect your project's dependencies, you can specify them manually from the commandline::

    prospector --uses django celery


Additionally, if Prospector is automatically detecting a library that you do not in fact use, you can turn off autodetection completely::

	prospector --no-autodetect


Note that as far as possible, these adaptors have been written as plugins or augmentations for the underlying tools so that they can be used without requiring Prospector. For example, the Django support is available as a pylint plugin. See the "Supported frameworks and libraries" section for more information.

Strictness
''''''''''

Prospector has a configurable 'strictness' level which will determine how harshly it searches for errors::

    prospector --strictness high


Possible values are ``verylow``, ``low``, ``medium``, ``high``, ``veryhigh``.

Prospector does not include documentation warnings by default, but you can turn this on using the ``--doc-warnings`` flag.


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
   :maxdepth: 2



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
