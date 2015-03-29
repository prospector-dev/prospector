Error Suppression
=================

Prospector profiles configuration via :doc:`profiles` which includes the ability
to tweak which errors are reported by the tools run by prospector. This is generally
where to make changes which affect the project as a whole.

It is also possible to suppress errors in specific places. In general the best place
to find out how to do this will be on the documentation site of the tool which generates
the error. This page contains additional information about behaviour which prospector adds.

Suppressing Pylint Errors
-------------------------

Pylint errors can be suppressed by adding a comment of the format::

    # pylint:disable=redefined-builtin

Although you can also use the numeric code (something like ``W1101``), pylint is moving towards
using symbolic names so it is better to use the full name for the error.

If Prospector finds that pylint would have emitted an error but a suppression comment disabled
the error, then all equivalent errors from other tools will also be suppressed. This is

Ignoring entire files
---------------------

Although the ideal method of ignoring files is by using the ``ignore-patterns`` and ``ignore-paths``
in a :doc:`profile <profiles>`, it is often the case that existing tools and configuration are
already present in a repository.

`flake8` includes the following directive to ignore an entire file, which is also honoured by
prospector::

    # flake8: noqa

``# noqa``
----------

A comment of ``noqa`` is used by `pep8` and `pyflakes` when ignoring all errors on a certain
line. If Prospector encounters a ``# noqa`` comment it will suppress any error from any tool
including ``pylint`` and others such as ``dodgy``.
