prospector
==========

.. image:: https://img.shields.io/pypi/v/prospector.svg
   :target: https://pypi.python.org/pypi/prospector
   :alt: Latest Version of Prospector
.. image:: https://github.com/PyCQA/prospector/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/PyCQA/prospector/actions/workflows/tests.yml
   :alt: Build Status
.. image:: https://img.shields.io/coveralls/PyCQA/prospector.svg?style=flat
   :target: https://coveralls.io/r/PyCQA/prospector
   :alt: Test Coverage
.. image:: https://readthedocs.org/projects/prospector/badge/?version=latest
   :target: https://prospector.readthedocs.io/
   :alt: Documentation


About
-----

Prospector is a tool to analyse Python code and output information about
errors, potential problems, convention violations and complexity.

It brings together the functionality of other Python analysis tools such as
`Pylint <https://docs.pylint.org/>`_,
`pycodestyle <https://pycodestyle.pycqa.org/>`_,
and `McCabe complexity <https://pypi.python.org/pypi/mccabe>`_.
See the `Supported Tools <https://prospector.readthedocs.io/en/latest/supported_tools.html>`_
documentation section for a complete list.

The primary aim of Prospector is to be useful 'out of the box'. A common complaint of other
Python analysis tools is that it takes a long time to filter through which errors are relevant
or interesting to your own coding style. Prospector provides some default profiles, which
hopefully will provide a good starting point and will be useful straight away, and adapts
the output depending on the libraries your project uses.

Installation
------------

Prospector can be installed from PyPI using ``pip`` by running the following command::

    pip install prospector

Optional dependencies for Prospector, such as ``pyroma`` can also be installed by running::

    pip install prospector[with_pyroma]

Some shells (such as ``Zsh``, the default shell of macOS Catalina) require brackets to be escaped::

    pip install prospector\[with_pyroma\]

For a list of all of the optional dependencies, see the optional extras section on the ReadTheDocs
page on `Supported Tools Extras <https://prospector.readthedocs.io/en/latest/supported_tools.html#optional-extras>`_.

For local development, `poetry <https://python-poetry.org/>`_ is used. Check out the code, then run::

    poetry install

And for extras::

    poetry install -E with_everything

For more detailed information on installing the tool, see the
`installation section <https://prospector.readthedocs.io/en/latest/#installation>`_ of the tool's main page
on ReadTheDocs.

Documentation
-------------

Full `documentation is available at ReadTheDocs <https://prospector.readthedocs.io>`_.

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
~~~~~~~~~~~~~

The default output format of ``prospector`` is designed to be human readable. For parsing
(for example, for reporting), you can use the ``--output-format json`` flag to get JSON-formatted
output.

Profiles
~~~~~~~~

Prospector is configurable using "profiles". These are composable YAML files with directives to
disable or enable tools or messages. For more information, read
`the documentation about profiles <https://prospector.readthedocs.io/en/latest/profiles.html>`_.

If your code uses frameworks and libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Often tools such as pylint find errors in code which is not an error, for example due to attributes of classes being
created at run time by a library or framework used by your project.
For example, by default, pylint will generate an error for Django models when accessing ``objects``, as the
``objects`` attribute is not part of the ``Model`` class definition.

Prospector mitigates this by providing an understanding of these frameworks to the underlying tools.

Prospector will try to intuit which libraries your project uses by
`detecting dependencies <https://github.com/landscapeio/requirements-detector>`_ and automatically turning on
support for the requisite libraries. You can see which adaptors were run in the metadata section of the report.

If Prospector does not correctly detect your project's dependencies, you can specify them manually from the commandline::

    prospector --uses django celery

Additionally, if Prospector is automatically detecting a library that you do not in fact use, you can turn
off autodetection completely::

    prospector --no-autodetect

Note that as far as possible, these adaptors have been written as plugins or augmentations for the underlying
tools so that they can be used without requiring Prospector. For example, the Django support is available as a pylint plugin.

Strictness
~~~~~~~~~~

Prospector has a configurable 'strictness' level which will determine how harshly it searches for errors::

    prospector --strictness high

Possible values are ``verylow``, ``low``, ``medium``, ``high``, ``veryhigh``.

Prospector does not include documentation warnings by default, but you can turn
this on using the ``--doc-warnings`` flag.

pre-commit
----------

If you'd like Prospector to be run automatically when making changes to files in your Git
repository, you can install `pre-commit <https://pre-commit.com/>`_ and add the following
text to your repositories' ``.pre-commit-config.yaml``:

.. code-block:: yaml

    repos:
    - repo: https://github.com/PyCQA/prospector
      rev: v1.16.1 # The version of Prospector to use, if not 'master' for latest
      hooks:
        - id: prospector

This only installs base prospector - if you also use optional tools, for example bandit and/or mypy, then you can add
them to the hook configuration like so:

.. code-block:: yaml

    repos:
    - repo: https://github.com/PyCQA/prospector
      rev: v1.16.1
      hooks:
        - id: prospector
          additional_dependencies:
            - ".[with_mypy,with_bandit]"
          args: [
            '--with-tool=mypy',
            '--with-tool=bandit',
            ]

Additional dependencies can be `individually configured <https://prospector.landscape.io/en/master/profiles.html#individual-configuration-options>`_ in your `prospector.yml` file :

.. code-block:: yaml

    # https://bandit.readthedocs.io/en/latest/config.html
    bandit:
    options:
        skips:
        - B201
        - B601
        - B610
        - B611
        - B703

    # https://mypy.readthedocs.io/en/stable/command_line.html
    mypy:
    options:
        ignore-missing-imports: true

For prospector options which affect display only - those which are not configurable using a profile - these can be
added as command line arguments to the hook. For example:

.. code-block:: yaml

    repos:
    - repo: https://github.com/PyCQA/prospector
      rev: v1.16.1
      hooks:
        - id: prospector
          additional_dependencies:
            - ".[with_mypy,with_bandit]"
          args:
            - --with-tool=mypy
            - --with-tool=bandit
            - --summary-only
            - --zero-exit



License
-------

Prospector is available under the GPLv2 License.
