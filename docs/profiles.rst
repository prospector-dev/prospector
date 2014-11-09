Profiles
========

The behaviour of prospector can be configured by creating a profile. A profile is
a YAML file containing several sections as described below.

If you have a ``.prospector.yaml`` or ``.prospector/prospector.yaml`` file in the
path that prospector is checking, it will automatically be loaded. Otherwise, you
can pass in the profile as an argument::

    prospector --profile /path/to/your/profile.yaml

You can also use a name instead of the path, if it is on the ``profile-path``::

    prospector --profile my_profile


.. _profile_path:

Profile Path
------------

The name of a profile is the filename without the ``.yaml`` extension. So if you create 
a profile called 'my_project.yaml', the name will be 'my_project'. Inheritance works
by searching the ``profile-path`` for files matching the name in the inheritance list.

The ``profile-path`` is where Prospector should search when looking for profiles. By
default, it will look in the directory containing the built-in profiles, as well as
the directory where prospector is running, and a `.prospector` directory relative to
that. To add additional places to search::

    prospector --profile-path path/to/your/profiles



Example
-------

Here is an example profile::
  
    output_format: json

    inherits:
      - no_test_warnings
      - strictness_medium

    ignore:
      - ^docs/

    pep8:
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
options. You can see the `full list on GitHub <https://github.com/landscapeio/prospector/tree/master/prospector/profiles/profiles>`_.


.. _strictness:

Strictness
``````````

There is a command line argument to tweak how picky Prospector will be::

    prospector --strictness

This is implemented using profiles, and is simply a list of messages to disable at each
level of strictness.


Inheritance
-----------

Profiles can inherit from other profiles, and can inherit from more than one profile. 
Prospector merges together all of the options in each profile, starting at the top
of the inheritance tree and overwriting values with those found lower. 

The example profile above inherits from the 'strictness_medium' profile provided by
prospector. It will take all options from 'strictness_medium' except where new settings
are defined, which will be used in preference.

For lists, such as the ``ignore`` section, they will be merged together rather than 
overwritten - so essentially, the ``ignore`` section will accumulate.

The profile named in the ``inherits`` section must be on the :ref:`profile path <profile_path>`.

Note that when using profiles, prospector does not automatically configure ``strictness``.
The assumption is that if you provide a profile, you provide all the information about which
messages to turn on or off. To keep the strictness functionality, simply inherit from the
built-in prospector profiles::

    inherits:
        - strictness_medium


Ignoring Paths
--------------

The ``ignore`` section is a list of regular expressions. The path of each directory and file
that prospector finds is passed to each regular expression and `searched`
(ie, ``re.search`` not ``re.match``). If any matches are found, the file or directory is not
included in the checks.


Tool Configuration
------------------

Each tool can be individually configured with a section beginning with the tool name 
(in lowercase). Valid values are 
``pylint``, ``pep8``, ``mccabe``, ``dodgy``, ``pyflakes``, ``frosted``, 
``vulture`` and ``pyroma``.

Enabling and Disabling Tools
````````````````````````````
There are :doc:`6 default and 2 optional <supported_tools>`. Unless otherwise configured,
the defaults are enabled and the optional tools are disabled.

In a profile, you can enable or disable a tool using the boolean ``run``::

    pyroma:
      run: true

Note that the ``--tools`` :doc:`command line argument <usage>` overrides profiles if used.



Enabling and Disabling Messages
```````````````````````````````

Messages can be enabled or disabled using the tool's code for the output. These codes are
either from the tool itself, or provided by prospector for those tools which do not have
message codes. The list of tools and message codes can be found 
`in the tools package <https://github.com/landscapeio/prospector/tree/master/prospector/tools>`_.

The typical desired action is to disable messages::

    pylint:
      disable:
        - E0202
        - E0203

However, you can also enable messages which were disabled by parent profiles::

    pylint:
      enable:
        - E0202
        - E0203


Tool Options
````````````

Some tools can be further configured or tweaked using an options hash::

    pep8:
      options:
        max-line-length: 120

The available options are:

+-----------+------------------+----------------------------------------------+
| Tool      + Option Name      + Possible Values                              |
+===========+==================+==============================================+
| mccabe    | max-complexity   | Maximum number of paths allowed in a method  |
+-----------+------------------+----------------------------------------------+
| pep8      | max-line-length  | Maximum line length allowed                  |
+-----------+------------------+----------------------------------------------+
| pylint    | -anything-       | Any of the `pylint options`_                 |
+-----------+------------------+----------------------------------------------+


.. _pylint options: http://docs.pylint.org/features.html#options
