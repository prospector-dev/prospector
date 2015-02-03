Supported Tools
===============

Prospector currently supports 10 tools, of which 7 are defaults and 3 are optional extras.

Enabling or Disabling Tools
---------------------------

Prospector will run with defaults enabled and optional extras disabled unless configured otherwise.

To specify an exact list of tools to run, for example, only pylint and pep8::

    prospector --tool pylint --tool pep8 

Note that this command line option will override values set in :doc:`profiles<profiles>`.

To specify optional extras on top of the defaults, for example, to run defaults and also pyroma without needing to specify the complete list of defaults::

    prospector --with-tool pyroma

To run the default tools but turn off one or two defaults::

    prospector --without-tool mccabe


Defaults
--------

`Pylint <http://www.pylint.org>`_
`````````````````````````````````
Pylint is the most comprehensive static analysis tool for Python. It is extremely thorough
and is the source of most messages that prospector outputs.


`pep8.py <http://pep8.readthedocs.org/en/latest/>`_
```````````````````````````````````````````````````

``pep8.py`` is a simple tool to warn about violations of the 
`PEP8 style guide <http://legacy.python.org/dev/peps/pep-0008/>`_. It produces
messages for any divergence from the style guide.

Prospector's concept of :doc:`strictness <profiles>` turns off various warnings 
depending on the strictness level. By default, several PEP8 errors will be
supressed. To adjust this without adjusting the strictness of other tools, you have
some options::

    # turn off pep8 checking completely:
    prospector --no-style-warnings

    # turn on complete pep8 checking:
    prospector --full-pep8

    # change the maximum line length allowed 
    # (the default varies by strictness):
    prospector --max-line-length 120


`pyflakes <https://launchpad.net/pyflakes>`_
````````````````````````````````````````````

Pyflakes analyzes programs and detects various errors. It is simpler and faster
than pylint, but also not as thorough.


`mccabe <https://github.com/flintwork/mccabe>`_
```````````````````````````````````````````````
`McCabe or cyclomatic complexity <http://en.wikipedia.org/wiki/Cyclomatic_complexity>`_ is
a measurement of how many paths there are in a given function or method. It measures how
complicated your functions are, and warns if they reach a certain threshold. Methods that
are too complex are prone to logic errors, and should be refactored to a series of smaller
methods.


`dodgy <https://github.com/landscapeio/dodgy>`_
```````````````````````````````````````````````

Dodgy is a very simple tool designed to find 'dodgy' things which should
not be in a public project, such as secret keys, passwords, AWS tokens or 
source control diffs.

`pep257 <https://github.com/GreenSteam/pep257>`_
````````````````````````````````````````````````

``pep257`` is a simple tool to warn about violations of the
`PEP257 Docstring Conventions <http://legacy.python.org/dev/peps/pep-0257/>`_.
It produces messages for any divergence from the style guide.

This tool is currently considered *experimental* due to some bugs in its
ability to parse code. For example, modules that contain an ``__all__`` could
end up producing bogus error messages if the ``__all__`` isn't formatted
exactly as ``pep257`` expects it.

It will not run by default, and must be enabled explicitly (via ``--with-tool pep257``
or in a :doc:`profile <profiles>`) or implicitly (using the ``--doc-warnings`` flag).


`profile-validator`
```````````````````

This is a simple tool built in to prospector which validates
:doc:`prospector profiles <profiles>`.




Optional Extras
---------------

These extras are integrated into prospector but are not activated by default.
This is because their output is not necessarily useful for all projects.

They are also not installed by default. The instructions for installing each tool is in the tool 
section below. To install all extras at the same time, install prospector using the ``with_everything`` option::

    pip install prospector[with_everything]


`Pyroma <https://bitbucket.org/regebro/pyroma>`_
````````````````````````````````````````````````
Pyroma is a tool to check your `setup.py` to ensure it is following best practices
of the Python packaging ecosystem. It will warn you if you are missing any package 
metadata which would improve the quality of your package. This is recommended if you
intend to publish your code on PyPI.

To install and use::

    pip install prospector[with_pyroma]
    prospector --with-tool pyroma


`Vulture <https://bitbucket.org/jendrikseipp/vulture>`_
```````````````````````````````````````````````````````

Vulture finds unused classes, functions and variables in your code. This could
be useful if your project is an application rather than a library, however, if
you do a lot of dynamic access or metaprogramming, Vulture will likely warn 
about unused code that is in fact used.

To install and use::

    pip install prospector[with_vulture]
    prospector --with-tool vulture


`frosted <https://github.com/timothycrosley/frosted>`_
``````````````````````````````````````````````````````
Frosted is a fork of pyflakes which was created with the intention of taking over
from and extending pyflakes as development had slowed. Since Prospector was originally
created, pyflakes development has started up again and frosted has stagnated, so it has
been demoted to be an optional extra.

To install and use::

    pip install prospector[with_frosted]
    prospector --with-tool frosted
