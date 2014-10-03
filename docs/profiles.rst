Profiles
========

Here is an example profile::
  
    inherits:
      - no_test_warnings
      - strictness_medium

    ignores:
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


Inheritance
-----------

Profiles can inherit from other profiles, and can inherit from more than one profile. 
Prospector merges together all of the options in each profile, starting at the top
of the inheritance tree and overwriting values with those found lower. 

The example profile above inherits from the 'strictness_medium' profile provided by
prospector. It will take all options from 'strictness_medium' except where new settings
are defined, which will be used in preference.

For lists, such as the ``ignores`` section, they will be merged together rather than 
overwritten - so essentially, the ignores section will accumulate.

The name of a profile is the filename without the ``.yaml`` extension. So if you create 
a profile called 'my_project.yaml', the name will be 'my_project'. Inheritance works
by searching the ``profile-path`` for files matching the name in the inheritance list.

The ``profile-path`` is where Prospector should search when looking for profiles. By
default, it will look in the directory containing the built-in profiles, as well as
the directory where prospector is runing, and a `.prospector` directory relative to
that. To add additional places to search::

    prospector --profile-path path/to/your/profiles


Ignoring Paths
--------------

The ``ignores`` section is a list of regular expressions. The path of each directory and file
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
`in the tools package<https://github.com/landscapeio/prospector/tree/master/prospector/tools>`_.

The typical desired action is to disable messages::

    pylint:
      disable:
        - E0202
        - E0203

However, you can also enable messages which were disabled by parent profiles:

    pylint:
      enable:
        - E0202
        - E0203


Tool Options
````````````

