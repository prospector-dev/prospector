.. Prospector documentation master file, created by
   sphinx-quickstart on Sun Sep 28 11:26:59 2014.

Prospector - Python Static Analysis
===================================

About
-----

.. image:: https://img.shields.io/pypi/v/prospector.svg
   :target: https://pypi.python.org/pypi/prospector
   :alt: Latest Version of Prospector
.. image:: https://github.com/PyCQA/prospector/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/PyCQA/prospector/actions/workflows/tests.yml
   :alt: Build Status
.. image:: https://img.shields.io/coveralls/PyCQA/prospector.svg?style=flat
   :target: https://coveralls.io/r/PyCQA/prospector
   :alt: Test Coverage


Prospector is a tool to analyse Python code and output information about errors, potential problems, convention violations and complexity.

It brings together the functionality of other Python analysis tools such as `Pylint`_, `pycodestyle`_, and `McCabe complexity`_.
See the :doc:`Supported Tools<supported_tools>` section for a complete list of default and optional extra tools.

The primary aim of Prospector is to be useful 'out of the box'. A common complaint of other
Python analysis tools is that it takes a long time to filter through which errors are relevant
or interesting to your own coding style. Prospector provides some default profiles, which
hopefully will provide a good starting point and will be useful straight away,
and adapts the output depending on the libraries your project uses.

.. _pylint: https://pylint.readthedocs.io/
.. _pycodestyle: https://pycodestyle.pycqa.org/
.. _McCabe complexity: https://pypi.python.org/pypi/mccabe


Installation
------------

You can install default tools using ``pip`` command::

    pip install prospector


For a full list of optional extra tools, and specific examples to install each of them,
see the :doc:`page on supported tools <supported_tools>`.

For example to install an optional tool such as ``pyroma``::

    pip install prospector[with_pyroma]


.. Note::

   Some shells (such as ``Zsh``, the default shell of macOS Catalina) require brackets to be escaped::

       pip install prospector\[with_pyroma\]


To install two or more optional extra tools at the same time, they must be comma separated (and without spaces).
For example to install mypy and bandit::

    pip install prospector[with_mypy,with_bandit]


And to install all optional extra tools at the same time, install prospector using the ``with_everything`` option::

    pip install prospector[with_everything]


For best results, you should install prospector to the same place as your project and its dependencies. That is,
if you are using virtual environments, install prospector into that virtual environment alongside your code. This
allows the underlying tools to give better results, as they can infer and use knowledge of libraries that you use.
If you install prospector system-wide and use it on a project in a virtual environment, you will see several
incorrect errors because prospector cannot access the libraries your project uses.


Usage
-----

Simply run prospector from the root of your project::

    prospector


This will output a list of messages pointing out potential problems or errors, for example::

    prospector.tools.base (prospector/tools/base.py):
        L5:0 ToolBase: pylint - R0922
        Abstract class is only referenced 1 times

Read about the full list of options in the :doc:`usage <usage>` page.

It is also possible to use prospector as a :doc:`pre-commit hook <pre-commit>`.


Behaviour
---------

Adapting to Dependencies
````````````````````````

Prospector will `try to detect <https://github.com/landscapeio/requirements-detector>`_ the
libraries that your project uses, and adapt the output and filtering to those libraries.
For example, if you use Django, the
`pylint-django <https://github.com/PyCQA/pylint-django>`_ plugin will be loaded
to help Pylint inspect Django-specific code.

There is currently support for the following frameworks:

- `Celery <https://github.com/PyCQA/pylint-celery>`_
- `Django <https://github.com/PyCQA/pylint-django>`_
- `Flask <https://github.com/jschaf/pylint-flask>`_

If you have a suggestion for another framework or library which should be supported,
please `add an issue <https://github.com/PyCQA/prospector/issues>`_
or :doc:`consider creating a pull request <contrib>`.


Strictness
``````````

Prospector can be configured to be more or less strict. The more strict, the more errors and
warnings it will find. At higher strictness levels, you may find that the output is a bit too
picky. The default level is designed to give useful output and warnings but also to suppress
messages which are not necessarily useful.

To change the strictness level::

    prospector --strictness high

Valid levels are ``verylow``, ``low``, ``medium``, ``high`` and ``veryhigh``.


Profiles
````````

A profile is a YAML file containing various directives about which messages and which tools
to allow or disable. Profiles can inherit from each other, allowing you to adapt the behaviour
of existing profiles or compose several smaller specialised profiles into one to suit your
project.

Note that the 'strictness' is implemented as a profile.

There is more detail about profiles and how to use them on
:doc:`the profiles documentation <profiles>` page.


Pre-commit Hook
```````````````

Prospector can be configured as a `pre-commit <https://pre-commit.com>`_ hook.

For more information see :doc:`the pre-commit documentation <pre-commit>`.


License
-------

Prospector is available under the GPLv2 License.
