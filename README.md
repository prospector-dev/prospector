prospector
==========

[![Latest Version](https://img.shields.io/pypi/v/prospector.svg)](https://pypi.python.org/pypi/prospector)
[![Build Status](https://travis-ci.org/landscapeio/prospector.png?branch=master)](https://travis-ci.org/landscapeio/prospector) 
[![Health](https://landscape.io/github/landscapeio/prospector/master/landscape.svg?style=flat)](https://landscape.io/github/landscapeio/prospector/master)
[![Coverage Status](https://img.shields.io/coveralls/landscapeio/prospector.svg?style=flat)](https://coveralls.io/r/landscapeio/prospector)
[![Documentation](https://readthedocs.org/projects/prospector/badge/?version=master)](http://prospector.landscape.io/)

# About

Prospector is a tool to analyse Python code and output information about errors, potential problems, convention violations and complexity.

It brings together the functionality of other Python analysis tools such as [pylint](http://pylint.org), [pep8](https://pypi.python.org/pypi/pep8) and [McCabe complexity](https://pypi.python.org/pypi/mccabe). More information and a complete list of supported tools is available on [the documentation site](http://prospector.readthedocs.org/en/latest/supported_tools.html).

The primary aim of Prospector is to be useful 'out of the box'. A common complaint of other Python analysis tools is that it takes a long time to filter through which errors are relevant or interesting to your own coding style. Prospector provides some default profiles, which hopefully will provide a good starting point and will be useful straight away, and adapts the output depending on the libraries your project uses.

# Installation

Prospector can be installed using `pip` by running the following command:

```
pip install prospector
```

Optional dependencies for Prospector, such as `pyroma` can also be installed by running:

```
pip install prospector[with_pyroma]
```

For a list of all of the optional dependencies, see the optional extras section on the ReadTheDocs page on [supported tools](https://prospector.landscape.io/en/latest/supported_tools.html#optional-extras).

For more detailed information on installing the tool, see the [installation section](http://prospector.landscape.io/en/latest/#installation) of the tool's main page on ReadTheDocs.

# Documentation

Full [documentation is available at ReadTheDocs](http://prospector.landscape.io).

# Usage

Simply run prospector from the root of your project:

```
prospector
```

This will output a list of messages pointing out potential problems or errors, for example:

```
prospector.tools.base (prospector/tools/base.py):
    L5:0 ToolBase: pylint - R0922
    Abstract class is only referenced 1 times
```

## Options

Run `prospector --help` for a full list of options and their effects.

### Output Format

The default output format of `prospector` is designed to be human readable. For parsing (for example, for reporting), you can use the `--output-format json` flag to get JSON-formatted output.

### Profiles

Prospector is configurable using "profiles". These are composable YAML files with directives to disable or enable tools or messages. For more information, read [the documentation about profiles](http://prospector.landscape.io/en/latest/profiles.html)

### If your code uses frameworks and libraries

Often tools such as pylint find errors in code which is not an error, due to, for example, attributes of classes being created at run time by a library or framework used by your project. For example, by default, pylint will generate an error for Django models when accessing `objects`, as the `objects` attribute is not part of the `Model` class definition. 

Prospector mitigates this by providing an understanding of these frameworks to the underlying tools.

Prospector will try to intuit which libraries your project uses by [detecting dependencies](https://github.com/landscapeio/requirements-detector) and automatically turning on support for the requisite libraries. You can see which adaptors were run in the metadata section of the report.

If Prospector does not correctly detect your project's dependencies, you can specify them manually from the commandline:

```
prospector --uses django celery
```

Additionally, if Prospector is automatically detecting a library that you do not in fact use, you can turn off autodetection completely:

```
prospector --no-autodetect
```

Note that as far as possible, these adaptors have been written as plugins or augmentations for the underlying tools so that they can be used without requiring Prospector. For example, the Django support is available as a pylint plugin.

### Strictness

Prospector has a configurable 'strictness' level which will determine how harshly it searches for errors.

```
prospector --strictness high
```

Possible values are `verylow`, `low`, `medium`, `high`, `veryhigh`.

Prospector does not include documentation warnings by default, but you can turn this on using the `--doc-warnings` flag.


# License

Prospector is available under the GPLv2 License.
