Pre-commit Hook
===============

If you'd like Prospector to be run automatically when making changes to files in your Git
repository, you can install `pre-commit`_ and add the following
text to your repositories' ``.pre-commit-config.yaml``::

    repos:
    -   repo: https://github.com/PyCQA/prospector
        rev: 1.10.0 # The version of Prospector to use, if not 'master' for latest
        hooks:
        -   id: prospector

.. _pre-commit: https://pre-commit.com/

Commandline Arguments
---------------------

Some controls for prospector, especially surrounding how the output is displayed, are not
:doc:`configurable from a profile <profiles>`, only from the commandline.

To add command-line arguments to the pre-commit hook config file::

    repos:
    -   repo: https://github.com/PyCQA/prospector
        rev: 1.10.0
        hooks:
        -   id: prospector
            args:
            - --summary-only


Optional Tools
--------------

By default the configuration will only install :doc:`the base supported tools <supported_tools>` and not optional tools.

If you also use optional tools, for example bandit or mypy, then you can add
them to the hook configuration like so::

    repos:
    -   repo: https://github.com/PyCQA/prospector
        rev: 1.10.0
        hooks:
        -   id: prospector
            additional_dependencies:
            - ".[with-mypy,with-bandit]"
          - args: [
            '--with-tool=mypy',
            '--with-tool=bandit',
            ]


This is equivalent to running::

    pip install prospector[with-bandit,with-mypy]
