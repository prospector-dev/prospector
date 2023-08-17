Profiles / Configuration
========================

The behaviour of prospector can be configured by creating a profile. A profile is
a YAML file containing several sections as described below.

Prospector will search for a ``.prospector.yaml`` file (and `several others`_) in the path that it is checking.
If found, it will automatically be loaded. Otherwise, you
can pass in the profile as an argument::

    prospector --profile /path/to/your/profile.yaml

You can also use a name instead of the path, if it is on the ``profile-path``::

    prospector --profile my_profile

In general, command-line arguments override and take precedence over values found
in profiles.

.. _several others: https://github.com/PyCQA/prospector/blob/master/prospector/profiles/__init__.py

.. _profile_path:


Profile Path
------------

The name of a profile is the filename without the ``.yaml`` extension. So if you create
a profile called 'my_project.yaml', the name will be 'my_project'. Inheritance works
by searching the ``profile-path`` for files matching the name in the inheritance list.

The ``profile-path`` is where Prospector should search when looking for profiles. By
default, it will look in the directory containing the `built-in profiles`_, as well as
the directory where prospector is running, and a ``.prospector`` directory relative to
that. To add additional places to search::

    prospector --profile-path path/to/your/profiles


.. _built-in profiles: https://github.com/PyCQA/prospector/tree/master/prospector/profiles/profiles



Example
-------

Here is an example profile::

    output-format: json

    strictness: medium
    test-warnings: true
    doc-warnings: false

    inherits:
      - my/other/profile.yml

    ignore-paths:
      - docs

    ignore-patterns:
      - (^|/)skip(this)?(/|$)

    pycodestyle:
      disable:
        - W602
        - W603
      enable:
        - W601
      options:
        max-line-length: 79

    mccabe:
      run: false


Builtin Profiles
----------------

Prospector comes with several built-in profiles, which power some of strictness and style
options. You can see the `full list on GitHub <https://github.com/PyCQA/prospector/tree/master/prospector/profiles/profiles>`_.

Global Configuration options
----------------------------
Global configuration options for tools are the following:

* output-format_
* strictness_
* test-warnings_
* doc-warnings_
* member-warnings_
* inherits_
* ignore-paths_
* ignore-patterns_
* autodetect_
* uses_
* max-line-length_


.. _output-format:

Output-format
.............
Same command line options are available.
See :doc:`Output format <usage>`

.. _strictness:

Strictness
..........

There is a command line argument to tweak how picky Prospector will be::

    prospector --strictness

This is implemented using profiles, and is simply a list of messages to disable at each
level of strictness.

If creating your own profile, you can use the ``strictness`` like so::

    strictness: medium

Valid values are 'verylow', 'low', 'medium' (the default), 'high' and 'veryhigh'. If you don't specify a
strictness value, then the default of 'medium' will be used. To avoid using any of Prospector's default
strictness profiles, set ``strictness: none``.



There are some aspects of analysis which can be turned on or off separately from the strictness or
individual tuning of the tools. Example:

.. _doc-warnings:

Documentation Warnings
......................

By default prospector will not produce warnings about missing documentation or
`docstring styleguide violations <https://www.python.org/dev/peps/pep-0257/>`_.
If you want to see these, use the ``--doc-warnings`` flag at runtime or include it in
your profile::

    doc-warnings: true

This will turn on the otherwise disabled ``pycodestyle`` tool.

.. _test-warnings:

Test Warnings
.............

Prospector will not inspect unit tests and test files by default. You can
turn this on using the ``--test-warnings`` flag or in your profile::

    test-warnings: true

.. _member-warnings:

Member Warnings
...............

Pylint generates warnings when you try to access an attribute of a class that does not exist, or
import a module that does not exist. Unfortunately it is not always accurate and in some projects,
this message is a large amount of noise. Prospector therefore turns these messages off by default,
but you can turn it on using the ``--member-warnings`` flag or in a profile::

    member-warnings: true


.. _uses:
.. _autodetect:

Libraries Used and Autodetect
.............................

Prospector will adjust the behaviour of the underlying tools based on the libraries that your project
uses. If you use Django, for example, the `pylint-django <https://github.com/PyCQA/pylint-django>`_ plugin
will be loaded. This will happen automatically.

If prospector is not correctly determining which of its supported libraries you use, you can specify
it manually in the profile::

    uses:
        - django
        - celery
        - flask

Currently, Django, Flask and Celery have plugins.

If prospector is incorrectly deciding that you use one of these, you can turn off autodetection::

    autodetect: false


.. _inherits:

Inheritance
...........

Profiles can inherit from other profiles, and can inherit from more than one profile.
Prospector merges together all of the options in each profile, starting at the top
of the inheritance tree and overwriting values with those found lower.

The example profile above inherits from another profile provided by the user,
``my/other/profile.yml``. This allows you to have, for example, a project wide
default profile with specific overrides for each individual repository or library.

It is possible to inherit from the built-in prospector profiles as well, although
there are shortcuts for most of the built-ins, see below.::

    inherits:
        - strictness_medium
        - full_pep8

For lists, such as the ``ignore`` section, they will be merged together rather than
overwritten - so essentially, the ``ignore`` section will accumulate.

The profile named in the ``inherits`` section must be on the :ref:`profile path <profile_path>`.

Inheritance can also be optional - for example, if each developer might have a local prospector configuration
but that's not guaranteed, then you can inherit from a profile with the ``?`` suffix and if it is not present,
prospector will simply carry on. For example::

    inherits:
        - project_config
        - local_config?

In this case, if a developer has a local profile called 'local_config' it would append to the project-wide configuration,
but if they don't, prospector won't error with a ``ProfileNotFound`` exception.

Note that when using profiles, prospector does not automatically configure ``strictness``.
The assumption is that if you provide a profile, you provide all the information about which
messages to turn on or off. To keep the strictness functionality, simply inherit from the
built-in prospector profiles::

    inherits:
        - strictness_medium

The ``inherits`` file can also be in an external package, if you specify a name Prospector will search for a tile named
``prospector.yaml`` or ``prospector.yml`` in the module ``prospector-profile-<name>``. And if the name contains a ``:``
this mean that we use the syntax ``<module>:<file>`` to search the file named ``<file>.yaml`` or ``<file>.yml``
in the module name ``prospector-profile-<module>``. For example::

    inherits:
        - my_module
        - my_module:my_file

.. _ignore-paths:
.. _ignore-patterns:

Ignoring Paths and patterns
...........................

There are two ways to ignore paths or files.

Firstly, with the ``ignore-paths`` section. This is a list of paths to ignore relative to the repository root.
It can be a directory, in which case the directory contents and all subdirectories are ignored, or it can be a
specific file. For example, ``docs`` would ignore a directory in the repository root called "docs", while
``mypackage/vendor`` would ignore anything in the directory at "mypackage/vendor".

Secondly, ``ignore-patterns`` is a list of regular expressions. The relative path of files and directories is *searched*
for each regular expression, and ignored if any matches are found. If the expression matches a directory, the directory
contents and all subdirectories are ignored. For example, ``^example/doc_.*\.py$`` would ignore any files in the
"example" directory beginning with "doc\_". Another example: ``(^|/)docs(/|$)`` would ignore all directories called
"docs" in the entire repository.

Note that a further option called ``ignore`` is available. This is equivalent to ``ignore-patterns``, and is from
an older version of the configuration. It will continue working, but it is deprecated, and you should update
your profile if you are using it.

.. _max-line-length:

Max Line Length
...............
This general option, provides a way to select maximum line length allowed.

.. Note:: This general option overrides and takes precedence over same option in a particular tool (pycodestyle or pylint)



Individual Configuration Options
--------------------------------

Each tool can be individually configured with a section beginning with the tool name
(in lowercase). Valid values are ``bandit``, ``dodgy``, ``frosted``, ``mccabe``, ``mypy``, ``pydocstyle``, ``pycodestyle``,
``pyflakes``, ``pylint``, ``pyright``, ``pyroma`` and  ``vulture``.

Enabling and Disabling Tools
............................
There are :doc:`7 default and 5 optional <supported_tools>`. Unless otherwise configured,
the defaults are enabled and the optional tools are disabled.

In a profile, you can enable or disable a tool using the boolean ``run``::

    pyroma:
      run: true

Note that the ``--tools`` :doc:`command line argument <usage>` overrides profiles if used.



Enabling and Disabling Messages
...............................

Messages can be enabled or disabled using the tool's code for the output. These codes are
either from the tool itself, or provided by prospector for those tools which do not have
message codes. The list of tools and message codes can be found
`in the tools package <https://github.com/PyCQA/prospector/tree/master/prospector/tools>`_.

The typical desired action is to disable messages::

    pylint:
      disable:
        - method-hidden
        - access-member-before-definition

However, you can also enable messages which were disabled by parent profiles::

    pylint:
      enable:
        - method-hidden
        - access-member-before-definition

Pylint Plugins
..............

It is possible to specify list of plugins for Pylint. You can do this by using ``load-plugins``
option in ``pylint`` section::

    pylint:
        load-plugins:
            - plugin
            - plugin

Note that this option doesn't affect loading of :ref:`autodetected plugins <ignore-patterns>`.


PEP8 Control
............

The strictness will turn on or off different messages generated by the `pycodestyle <https://pycodestyle.pycqa.org>`_
tool depending on how picky they are. However, if you want to have the standard 'medium' strictness but get either
complete or zero pep8 style warnings, you can use a shorthand like below::

    pep8:
        full: true

Or::

    pep8:
        none: true

Note that this section is also the section for configuring the pycodestyle tool, see below. Therefore you can turn
on all warnings from pep8 but turn off just one or two individually or otherwise tweak the tool like so::

    pycodestyle:
        full: true
        disable:
            - E126
        options:
            max-line-length: 120

Tool Options
............

Some tools can be further configured or tweaked using an options hash::

    pycodestyle:
      options:
        max-line-length: 120

The available options are:

+----------------+------------------------+----------------------------------------------+
| Tool           + Option Name            + Possible Values                              |
+================+========================+==============================================+
| mccabe         | max-complexity         | Maximum number of paths allowed in a method  |
+----------------+------------------------+----------------------------------------------+
| pycodestyle    | max-line-length        | Maximum line length allowed (This option is  |
|                |                        | overridden by global option max-line-length_)|
+----------------+------------------------+----------------------------------------------+
| pylint         | -anything-             | Any of the `pylint options`_                 |
+----------------+------------------------+----------------------------------------------+
| mypy           | strict                 | strict mode                                  |
+----------------+------------------------+----------------------------------------------+
| mypy           | follow-imports         | How to treat imports                         |
+----------------+------------------------+----------------------------------------------+
| mypy           | ignore-missing-import  | Silently ignore imports of missing modules   |
+----------------+------------------------+----------------------------------------------+
| mypy           | platform               | Check for the given platform                 |
+----------------+------------------------+----------------------------------------------+
| mypy           | python-version         | assume it will be running on Python x.y      |
+----------------+------------------------+----------------------------------------------+
| mypy           | strict-optional        | Checking of Optional types and None values   |
+----------------+------------------------+----------------------------------------------+
| mypy           | namespace-packages     | Import discovery uses namespace packages     |
+----------------+------------------------+----------------------------------------------+
| mypy           | use-dmypy              | Use mypy daemon (mypy server) for faster     |
|                |                        | checks                                       |
+----------------+------------------------+----------------------------------------------+
| mypy           | check-untyped-defs     |Type check the interior of functions without  |
|                |                        |type annotations                              |
+----------------+------------------------+----------------------------------------------+
| bandit         | config                 | configuration filename                       |
+----------------+------------------------+----------------------------------------------+
| bandit         | profile                | profile to use                               |
+----------------+------------------------+----------------------------------------------+
| bandit         | severity               | report only issues of a given severity       |
+----------------+------------------------+----------------------------------------------+
| bandit         | confidence             | report only issues of a given confidence     |
+----------------+------------------------+----------------------------------------------+
| pyright        | level                  | Minimum diagnostic level (error or warning)  |
+----------------+------------------------+----------------------------------------------+
| pyright        | project                | Path to location of configuration file       |
+----------------+------------------------+----------------------------------------------+
| pyright        | pythonplatform         | Analyze for a specific platform (Darwin,     |
|                |                        | Linux, Windows)                              |
+----------------+------------------------+----------------------------------------------+
| pyright        | pythonversion          | Analyze for a specific version               |
+----------------+------------------------+----------------------------------------------+
| pyright        | skipunannotated        | Skip analysis of functions with no type      |
|                |                        | annotations                                  |
+----------------+------------------------+----------------------------------------------+
| pyright        | typeshed-path          | Path to location of typeshed type stubs      |
+----------------+------------------------+----------------------------------------------+
| pyright        | venv-path              | Directory that contains virtual environments |
+----------------+------------------------+----------------------------------------------+

See `mypy options`_ for more details

See `bandit options`_ for more details

See `pyright options`_ for more details



.. _pylint options: https://pylint.readthedocs.io/en/latest/user_guide/run.html
.. _bandit options: https://bandit.readthedocs.io/en/latest/config.html
.. _mypy options: https://mypy.readthedocs.io/en/stable/command_line.html
.. _pyright options: https://microsoft.github.io/pyright/#/command-line



Example
-------

Next is another example using most options::

    output-format: json

    strictness: medium
    test-warnings: true
    doc-warnings: false
    member-warnings: false
    inherits:
      - default
    ignore-paths:
      - docs
    ignore-patterns:
      - (^|/)skip(this)?(/|$)
    autodetect: true
    max-line-length: 88

    bandit:
      run: true
      options:
        config: .bandit.yml

    dodgy:
      run: true

    frosted:
      disable:
        - E103
        - E306

    mccabe:
      run: false
      options:
        max-complexity: 10

    pycodestyle:
      disable:
        - W602
        - W603
      enable:
        - W601
      options:
        max-line-length: 79

    pydocstyle:
      disable:
        - D100
        - D101

    pyflakes:
      disable:
        - F403
        - F810

    pylint:
      disable:
        - bad-builtin
        - too-few-public-methods
      options:
        max-locals: 15
        max-returns: 6
        max-branches: 15
        max-statements: 60
        max-parents: 7
        max-attributes: 7
        min-public-methods: 1
        max-public-methods: 20
        max-module-lines: 1000
        max-line-length: 99

    pyroma:
      disable:
        - PYR15
        - PYR18

    pyright:
      options:
        level: warning
        pythonversion: 3.7
        skipunannotated: true

    mypy:
      run: true
      options:
        ignore-missing-imports: true
        follow-imports: skip

    vulture:
      run: true
