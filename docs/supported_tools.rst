Supported Tools
===============

Prospector currently supports 12 tools, of which 7 are defaults and 5 are optional extras.

Enabling or Disabling Tools
---------------------------

Prospector will run with defaults enabled and optional extras disabled unless configured otherwise.

To specify an exact list of tools to run, for example, only pylint and pydocstyle::

    prospector --tool pylint --tool pydocstyle

Note that this command line option will override values set in :doc:`profiles<profiles>`.

To specify optional extras on top of the defaults, for example, to run defaults and also pyroma without needing to specify the complete list of defaults::

    prospector --with-tool pyroma

To run the default tools but turn off one or two defaults::

    prospector --without-tool mccabe


Defaults
--------

`Pylint <https://www.pylint.org>`_
```````````````````````````````````
Pylint is the most comprehensive static analysis tool for Python. It is extremely thorough
and is the source of most messages that prospector outputs.


`pycodestyle <https://pycodestyle.pycqa.org/en/latest/>`_
`````````````````````````````````````````````````````````

pycodestyle is a simple tool to warn about violations of the
`PEP8 style guide <https://www.python.org/dev/peps/pep-0008/>`_. It produces
messages for any divergence from the style guide.

Prospector's concept of :doc:`strictness <profiles>` turns off various warnings
depending on the strictness level. By default, several PEP8 errors will be
suppressed. To adjust this without adjusting the strictness of other tools, you have
some options::

    # turn off pep8 checking completely:
    prospector --no-style-warnings

    # turn on complete pep8 checking:
    prospector --full-pep8

    # change the maximum line length allowed
    # (the default varies by strictness):
    prospector --max-line-length 120


`Pyflakes <https://launchpad.net/pyflakes>`_
````````````````````````````````````````````

Pyflakes analyzes programs and detects various errors. It is simpler and faster
than pylint, but also not as thorough.


`Mccabe <https://github.com/PyCQA/mccabe>`_
```````````````````````````````````````````````
`McCabe or cyclomatic complexity <https://en.wikipedia.org/wiki/Cyclomatic_complexity>`_ is
a measurement of how many paths there are in a given function or method. It measures how
complicated your functions are, and warns if they reach a certain threshold. Methods that
are too complex are prone to logic errors, and should be refactored to a series of smaller
methods.


`Dodgy <https://github.com/landscapeio/dodgy>`_
```````````````````````````````````````````````

Dodgy is a very simple tool designed to find 'dodgy' things which should
not be in a public project, such as secret keys, passwords, AWS tokens or
source control diffs.

`Pydocstyle <https://github.com/PyCQA/pydocstyle>`_
```````````````````````````````````````````````````

Pydocstyle is a simple tool to warn about violations of the
`PEP257 Docstring Conventions <http://legacy.python.org/dev/peps/pep-0257/>`_.
It produces messages for any divergence from the style guide.

This tool is currently considered *experimental* due to some bugs in its
ability to parse code. For example, modules that contain an ``__all__`` could
end up producing bogus error messages if the ``__all__`` isn't formatted
exactly as ``pydocstyle`` expects it.

It will not run by default, and must be enabled explicitly (via ``--with-tool pep257``
or in a :doc:`profile <profiles>`) or implicitly (using the ``--doc-warnings`` flag).


`Profile-validator`
```````````````````

This is a simple tool built in to prospector which validates
:doc:`prospector profiles <profiles>`.




Optional Extras
---------------

These extras are integrated into prospector but are not activated by default.
This is because their output is not necessarily useful for all projects.

They are also not installed by default. The instructions for installing each tool is in the tool
section below. For more detailed information on installing, see :doc:`install section<index>`.

`Pyroma <https://github.com/regebro/pyroma>`_
`````````````````````````````````````````````
Pyroma is a tool to check your `setup.py` to ensure it is following best practices
of the Python packaging ecosystem. It will warn you if you are missing any package
metadata which would improve the quality of your package. This is recommended if you
intend to publish your code on PyPI.

To install and use::

    pip install prospector[with_pyroma]
    prospector --with-tool pyroma


`Vulture <https://github.com/jendrikseipp/vulture>`_
````````````````````````````````````````````````````

Vulture finds unused classes, functions and variables in your code. This could
be useful if your project is an application rather than a library, however, if
you do a lot of dynamic access or metaprogramming, Vulture will likely warn
about unused code that is in fact used.

To install and use::

    pip install prospector[with_vulture]
    prospector --with-tool vulture


`Mypy <https://github.com/python/mypy>`_
````````````````````````````````````````
Mypy is an experimental optional static type checker for Python that aims to combine
the benefits of dynamic (or "duck") typing and static typing. Mypy combines the
expressive power and convenience of Python with a powerful type system and
compile-time type checking.

To install and use::

    pip install prospector[with_mypy]
    prospector --with-tool mypy


`Bandit <https://github.com/PyCQA/bandit>`_
```````````````````````````````````````````
Bandit finds common security issues in Python code.

To install and use::

    pip install prospector[with_bandit]
    prospector --with-tool bandit


`Pyright <https://github.com/microsoft/pyright>`_
`````````````````````````````````````````````````

Pyright is a full-featured, standards-based static type checker for Python. It
is designed for high performance and can be used with large Python source bases.

To install and use::

    pip install prospector[with_pyright]
    prospector --with-tool pyright
