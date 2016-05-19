Command Line Usage
==================

.. _issue_16: https://github.com/landscapeio/prospector/issues/16

The simplest way to run prospector is from the project root with no arguments. It will try to figure everything else out itself and provide sensible defaults::

    prospector

You can specify a path to check::

    prospector path/to/my/package

And you can specify a list of python modules::

    prospector module/to/check.py
    prospector module/to/check.py other/module/to/check.py something/else.py

See below for :ref:`a complete list of options and flags<full_options>`. You can also run ``prospector --help`` for a full list of options and their effects.


Output Format
'''''''''''''

The default output format of ``prospector`` is designed to be human readable. You can change the output format using the ``--output-format`` or ``-o`` flags - for example, to get the output in JSON form you can use the ``--output-format json``.

+-------------+----------------------------------------------------------------------------+
| Format Name | Notes                                                                      |
+=============+============================================================================+
| ``emacs``   | | Support for emacs compilation output mode, see `issue_16`_.              |
+-------------+----------------------------------------------------------------------------+
| ``vscode``  | | Support for vscode python plugin                                         |
+-------------+----------------------------------------------------------------------------+
| ``grouped`` | | Similar to ``text``, but groups all message on the same line together    |
|             | | rather than having a separate entry per message.                         |
+-------------+----------------------------------------------------------------------------+
| ``pylint``  | | Produces output in the same style as ``pylint --parseable``. This should |
|             | | allow ``prospector`` to be used as a drop-in replacement for any tools   |
|             | | which parse ``pylint`` output. The one minor difference is that the      |
|             | | output includes the name of the tool which generated the error as well   |
|             | | as the error code.                                                       |
+-------------+----------------------------------------------------------------------------+
| ``json``    | | Produces a structured, parseable output of the messages and summary. See |
|             | | below for more information about the structure.                          |
+-------------+----------------------------------------------------------------------------+
| ``yaml``    | | Same as JSON except produces YAML output.                                |
+-------------+----------------------------------------------------------------------------+
| ``xunit``   | | Same as JSON except produces xunit compatile XML output.                 |
+-------------+----------------------------------------------------------------------------+
| ``text``    | | The default output format, a simple human readable format.               |
+-------------+----------------------------------------------------------------------------+


If your code uses frameworks and libraries
''''''''''''''''''''''''''''''''''''''''''

Often tools such as pylint find errors in code which is not an error, due to attributes of 
classes being created at run time by a library or framework used by 
your project. For example, by default, pylint will generate an error for Django 
models when accessing ``objects``, as the ``objects`` attribute is not part of the ``Model`` 
class definition. 

Prospector mitigates this by providing an understanding of these frameworks to the underlying 
tools.

Prospector will try to intuit which libraries your project uses by 
`detecting dependencies <https://github.com/landscapeio/requirements-detector>` 
and automatically turning on support for the requisite libraries. You can see which adaptors 
were run in the metadata section of the report.

If Prospector does not correctly detect your project's dependencies, you can specify them manually from the commandline::

    prospector --uses django celery flask


Additionally, if Prospector is automatically detecting a library that you do not in fact use, you can turn off autodetection completely::

	prospector --no-autodetect


Note that as far as possible, these adaptors have been written as plugins or augmentations for the underlying tools so that they can be used without requiring Prospector. For example, the Django support is available as a pylint plugin. See the "Supported frameworks and libraries" section for more information.

Strictness
''''''''''

Prospector has a configurable 'strictness' level which will determine how harshly it searches for errors::

    prospector --strictness high


Possible values are ``verylow``, ``low``, ``medium``, ``high``, ``veryhigh``.

Prospector does not include documentation warnings by default, but you can turn this on using the ``--doc-warnings`` flag.


.. _full_options:

All Options
'''''''''''

.. argparse::
   :module: prospector.run
   :func: get_parser
   :prog: prospector
