#########
Changelog
#########

Version 1.7.5 - WIP
-------------

Just say no to bugs.

**Fixes**:

* Stopped the ProfileValidator tool raising errors about ``pep8`` and ``pep257`` sections being unknown. Instead, they raise deprecated warnings.
* Blending works again - for example, pylint and pycodestyle errors representing the same thing are combined. After renaming pep8 to pycodestyle, this only worked when using legacy names.

**Tidyup**:

* Lots of warnings fixed from running prospector on itself

Version 1.7.4
-------------

Mea culpa release

**Fix**

The effort to allow pylint configuration in ``pyproject.toml`` to be used as an external config source (`issue here <https://github.com/PyCQA/prospector/issues/485>)`_ had the unintended side effect where any project using poetry would now use that configuration and thus would ignore the pylint configuration in the profile. This was true even if the ``pyproject.toml`` had no pylint directives in it.

The behaviour has now been fixed where pylint will be configured using configuration from the profile *first* and then if any additional settings are found in a ``pylintrc`` or ``pyproject.toml`` or ``setup.cfg`` then these will override the profile configuration, instead of replacing it entirely.

This also has the benefit of fixing `#227 <https://github.com/PyCQA/prospector/issues/227>`_.

Version 1.7.3
-------------

The war on bugs.

**Fixes**:

* Autodetect now does not die if a user does not have permissions (related to `#271 <https://github.com/PyCQA/prospector/issues/271>`_ and `#487 <https://github.com/PyCQA/prospector/issues/487>`_)
* Fixed that some pylint documentation warning messages were not correctly included in the list of documentation warnings to squash if doc warnings are not desired.
* Fixed the exit code for prospector - it was always ``0`` after the move to using poetry for packaging instead of ``1`` if errors were found (unless ``--zero-exit``) was used. This now exits with the correct code based on the documented (and previous) behaviour.
* Fix that ``pep8`` would overwrite instead of inherit from previous ``pycodestyle`` blocks, same with pep257 - `#491 (comment) <https://github.com/PyCQA/prospector/issues/491#issuecomment-1053539711>`_
* Fix the pre-commit hook, as it could not run without being installed ``[with_everything]``, due to the "NotAvailableTool" class not properly implementing the abstract base class.
* Improved documentation about the pre-commit hook as well to clarify its use better - `#484 <https://github.com/PyCQA/prospector/issues/484>`_


Version 1.7.2
-------------

More bugfixes!

**Fixes**:

* Fix that ``pep8`` and ``pep257`` sections were renamed but the old deprecated values were not properly used to configure ``pycodestyle`` and ``pydocstyle`` - `#491 <https://github.com/PyCQA/prospector/issues/491>`_
* Better handling for when the user running prospector is not able to read a file or directory - `#271 <https://github.com/PyCQA/prospector/issues/271>`_ and `#487 <https://github.com/PyCQA/prospector/issues/487>`_


Version 1.7.1
-------------

Lots of smaller bugfixes.

**Fixes**:

* Prospector now configures pylint using settings found in ``pyproject.toml`` or ``setup.cfg``, not only ``.pylintrc`` - `#485 <https://github.com/PyCQA/prospector/issues/485>`_
* Fixed ``--no-style-warnings`` command line argument no longer warning after renaming ``pep8`` to ``pycodestyle`` - `#488 <https://github.com/PyCQA/prospector/issues/488>`_
* Documentation is building again - `#473 <https://github.com/PyCQA/prospector/issues/473>`_
* ``--with-tool`` flag now respects - but overrides - tools disabled in profiles - `#447 <https://github.com/PyCQA/prospector/issues/447>`_
* Fixed crash with merging multiple import warnings - `#477 <https://github.com/PyCQA/prospector/issues/477>`_
* Fixed segfault when analysing code using cartopy - `#403 <https://github.com/PyCQA/prospector/issues/403>`_

Version 1.7.0
-------------

This is mostly a "tidying up" release.

**New**:

* Added a ``--quiet`` command line option to suppress all output. Useful if you just want to know the exit code of prospector for scripting.
* Removed the prospector "indent checker" since this is now no longer in pylint `#482 <https://github.com/PyCQA/prospector/issues/482>`_

**Fixes**:

`Deprecation warning:`

* Tools ``pep8`` and ``pep257`` have been renamed to ``pycodestyle`` and ``pydocstyle`` respectively. This is because the tools themselves were renamed years ago - See `#222 <https://github.com/PyCQA/prospector/issues/222>`_.

Note that this means that prospector profiles and message output uses this new name instead of the old name, so you will need to update your configuration. The old names will still work, but this legacy behaviour will be removed in prospector 2.0

* There is now a ``--legacy-tool-names`` flag for outputting pep8 or pep257 as the tool name when outputting errors. This is to be backwards compatible with any parsing logic; this flag is also deprecated and will go away in prospector 2.0

**Tidying up**

These are all internal prospector code quality improvements.

* `#467 <https://github.com/PyCQA/prospector/issues/467>`_ - Removed nosetests, as nose is not compatible with Python 3.10 yet and the pytest tests were already doing the same thing
* Tidied up the tox testing
* Started adding some type hints to methods
* Fixed lots of warnings raised by prospector when running prospector on itself...
* Removed some old python2 compatibility code which is no longer needed now python2 is not supported at all
* Fixed hyperlink formatting in this CHANGELOG to be RST (was never updated after converting from markdown)


Version 1.6.1
-------------

- Update pyflakes to 2.* `#454 <https://github.com/PyCQA/prospector/issues/454)>`_

Version 1.6.0
-------------

- Fixed incompatible version specification of pylint-plugin-utils. This now requires pylint-django of at least 2.5. `#478 <https://github.com/PyCQA/prospector/issues/478>`_

*note* This release drops support for python ``3.6.1``

Version 1.5.3 and 1.5.3dev0 and 1.5.3.1
---------------------------------------

- `#465 <https://github.com/PyCQA/prospector/issues/465>`_ Remove unnecessary configuration reset to fix pylint>=2.12 compatibility
- Version 1.5.3.1 was needed to unpin the pylint dependency to actually use the fix for compatibility.

Version 1.5.2
-------------

- `#465 <https://github.com/PyCQA/prospector/issues/465>`_ Bugfix release to pin pylint<2.12 because prospector's internals were not compatible with it

Version 1.5.1
-------------

- `#438 <https://github.com/PyCQA/prospector/issues/438>`_ Promoting pre-release to release as it appears to work

Version 1.5.0.1
---------------

- `#433 <https://github.com/PyCQA/prospector/issues/433>`_ Attempted fix of flake8 dependency versioning conflict

Version 1.5.0
-------------

- `#436 <https://github.com/PyCQA/prospector/pull/436>`_ Swapped out packaging to use poetry instead of setup.py and setuptools

Version 1.4.1
-------------

- `#373 <https://github.com/PyCQA/prospector/issues/373>`_ Permits to raise pylint's useless-suppression
- `#414 <https://github.com/PyCQA/prospector/pull/414>`_ Loosen pycodestyle requirement
- `#408 <https://github.com/PyCQA/prospector/pull/408>`_ Fix filenames if they are PosixPath
- `#412 <https://github.com/PyCQA/prospector/pull/412>`_ Fix unclosed file warning
- `#399 <https://github.com/PyCQA/prospector/pull/399>`_ Fix fatal error on running mypy when duplicate module names

Version 1.4.0
-------------

- `#424 <https://github.com/PyCQA/prospector/pull/424>`_ GitHub Action to discover typos with codespell
- `#421 <https://github.com/PyCQA/prospector/pull/421>`_ Loosen pylint requirement
- `#427 <https://github.com/PyCQA/prospector/pull/427>`_ Fix prospector for latest pylint version and add Github actions

Version 1.3.1
-------------
- `#390 <https://github.com/PyCQA/prospector/pull/390>`_ Updating Vulture API usage for newer versions of Vulture
- `#394 <https://github.com/PyCQA/prospector/pull/394>`_ Update pylint and pylint-django

Version 1.3.0
-------------
- Update pylint support to 2.5.2
- Update pylint-django to 2.0.15
- Update pyflakes support to 2.2.0
- Update pycodestyle support to 2.6.0
- Update pep8-naming support to 0.10.0
- Update pyflakes to <2.3.0 and >=2.2.0
- Update pycodestyle to <2.7.0 and >=2.6.0
- Update vulture to 1.5
- Drop Python 2 support
- Add output-target field when merging profiles
- Add support for [pycodestyle] external config section
- Fix AttributeExceptionError being raised when ignore_paths is an integer
- Use black on entire project
- Add new pylint option: `use_pylint_default_path_finder` to make sure there's an option to preserve pylint default behavior.
- Update pyflakes error code list to the recent version

Version 1.2.0
-------------
- Drop Python 3.4 support
- `#308 <https://github.com/PyCQA/prospector/pull/308>`_ Update pyflakes support to < 2.1.0
- `#324 <https://github.com/PyCQA/prospector/pull/324>`_ Add bandit support
- `#344 <https://github.com/PyCQA/prospector/pull/344>`_ Ignore __pycache__ and node_modules
- `#349 <https://github.com/PyCQA/prospector/pull/349>`_ and `#355 <https://github.com/PyCQA/prospector/pull/355>`_ Fix compatibility issues with mypy >= 0.730
- `#356 <https://github.com/PyCQA/prospector/pull/356>`_ Add support for Python 3.8

Version 1.1.7
-------------

- `#299 <https://github.com/PyCQA/prospector/pull/299>`_ Output path tests and abspaths for windows
- `#300 <https://github.com/PyCQA/prospector/pull/300>`_ Fix `check_paths` definition for pep8tool
- `#318 <https://github.com/PyCQA/prospector/pull/318>`_ Add support pylint --load-plugins option in profile
- `#336 <https://github.com/PyCQA/prospector/pull/336>`_ Pylint fix for message definitions usage
- `#340 <https://github.com/PyCQA/prospector/pull/340>`_ Bump pylint django
- `#343 <https://github.com/PyCQA/prospector/pull/343>`_ Support more kinds of mypy messages
- `@5ea0e95 <https://github.com/PyCQA/prospector/pull/342/commits/5ea0e95ac28db0911e37bc07be036c27078591b4>`_ Pin astroid to 2.2.5

Version 1.1.6.4
---------------
- `#333 <https://github.com/PyCQA/prospector/pull/333>`_ Hotfix for pylint module run
- `#309 <https://github.com/PyCQA/prospector/pull/309>`_ Remove the pylint locally-enabled message suppression

Version 1.1.6.2
---------------
- `#304 <https://github.com/PyCQA/prospector/pull/304>`_ Pin pylint to 2.1.1 for now as prospector is not compatible with 2.2.0
- `#302 <https://github.com/PyCQA/prospector/issues/302>`_ Pin astroid to 2.0.4 as pylint-django and pylint-flask need fixes to be compatible with newer versions

Version 1.1.6.1
---------------
- `#292 <https://github.com/PyCQA/prospector/issues/292>`_ Adding pylint plugin dependencies back and fixing autodetect behaviour.
- (note: .1 added as 1.1.6 upload to PyPI was broken)

Version 1.1.5
-------------
- `#283 <https://github.com/PyCQA/prospector/pull/283>`_ Remove unexpected argument from read_config_file - Remove quiet argument
- `#291 <https://github.com/PyCQA/prospector/pull/291>`_ Update pycodestyle support until 2.4.0
- `#280 <https://github.com/PyCQA/prospector/pull/280>`_ Add strict option and fixed emacs output format for mypy tool
- `#282 <https://github.com/PyCQA/prospector/pull/282>`_ Fix working dir detection

Version 1.1.4
---------------
- `#285 <https://github.com/PyCQA/prospector/issues/285>`_ Fix dependency tree resolution - now insists on `pep8-naming<=0.4.1` as later versions cause conflicting versions of flake8 to be installed.

Version 1.1.3
---------------
- `#279 <https://github.com/PyCQA/prospector/issues/279>`_ Fix --show-profile crash

Version 1.1.2
---------------
- `#276 <https://github.com/PyCQA/prospector/issues/276>`_ Updating required Pyroma version and removing some warnings which were removed from Pyroma - thanks `@volans- <https://github.com/volans->`_ for PR `#277 <https://github.com/PyCQA/prospector/pull/277>`_

Version 1.1.1
---------------
- Removing `pylint-common <https://github.com/landscapeio/pylint-common>`_ as a direct dependency as it does not add a lot of utility and is not kept up to date as much as other plugins

Version 1.1
---------------
- `#267 <https://github.com/PyCQA/prospector/pull/267>`_ Fix read_config_file using quiet keyword with older pylint versions
- `#262 <https://github.com/PyCQA/prospector/pull/262>`_ Bugfix report different behavior based on path(includes KeyError on FORMATTERS fix)

Version 1.0
---------------
- `#228 <https://github.com/PyCQA/prospector/pull/228>`_ Add mypy support
- `#249 <https://github.com/PyCQA/prospector/pull/249>`_ Add option to point to pylintrc inside prospector configuration file
- `#250 <https://github.com/PyCQA/prospector/pull/250>`_ Add option to redirect prospector output to files
- `#261 <https://github.com/PyCQA/prospector/pull/261>`_ Drop Python 3.3 support
- `#261 <https://github.com/PyCQA/prospector/pull/261>`_ Use Pylint >= 2 for Python 3

Version 0.12.11
---------------
- `#256 <https://github.com/PyCQA/prospector/pull/256>`_ Match relative paths that giving different results when using `--absolute-paths` flag
- Pin vulture version < 0.25

Version 0.12.10
---------------
- Force pyroma >= 2.3
- `#236 <https://github.com/PyCQA/prospector/pull/236>`_ Fix typo and update URLs in docs

Version 0.12.9
---------------
- `#237 <https://github.com/PyCQA/prospector/pull/237>`_ Load pylint plugins before pylint config
- `#253 <https://github.com/PyCQA/prospector/issues/253>`_ Relaxing pyroma constraint
- `#229 <https://github.com/PyCQA/prospector/issues/229>`_ prospector crashes on startup if a recent pyroma is installed

Version 0.12.8
---------------
* Enforece pylint, pyflakes and pycodestyle versions to avoid breaking other dependent tools
* `#242 <https://github.com/PyCQA/prospector/pull/248>`_ Fix absolute path issue with pylint
* `#234 <https://github.com/PyCQA/prospector/pull/234>`_ Added Python 3.5/3.6 support on build

Version 0.12.7
---------------
* Enforcing pydocstyle >= 2.0.0 for API compatibility reliability

Version 0.12.6
---------------
* `#210 <https://github.com/PyCQA/prospector/issues/210/>`_ `#212 <https://github.com/PyCQA/prospector/issues/212/>`_ Removing debug output accidentally left in (@souliane)
* `#211 <https://github.com/PyCQA/prospector/issues/211/>`_ Added VSCode extension to docs (@DonJayamanne)
* `#215 <https://github.com/PyCQA/prospector/pull/215/>`_ Support `pydocstyle>=2.0` (@samspillaz)
* `#217 <https://github.com/PyCQA/prospector/issues/217/>`_ Updating links to supported tools in docs (@mbeacom)
* `#219 <https://github.com/PyCQA/prospector/pull/219/>`_ Added a `__main__.py` to allow calling `python -m prospector` (@cprogrammer1994)

Version 0.12.5
---------------
* `#207 <https://github.com/PyCQA/prospector/pull/207/>`_ Fixed missing 'UnknownMessage' exception caused by recent pylint submodule changes
* Minor documentation formatting updates
* `#202 <https://github.com/PyCQA/prospector/issues/202/>`_ Ignoring .tox directories to avoid accidentally checking the code in there
* `#205 <https://github.com/PyCQA/prospector/pull/205/>`_ Fixes for compatibility with pylint 1.7+
* `#193 <https://github.com/PyCQA/prospector/pull/193/>`_ Fixes for compatibility with pylint 1.6+
* `#194 <https://github.com/PyCQA/prospector/pull/194/>`_ Fixes for compatibility with vulture 0.9+
* `#191 <https://github.com/PyCQA/prospector/pull/191/>`_ Fixes for compatibility with pydocstyle 1.1+

Version 0.12.4
---------------
* Panicky stapling of pyroma dependency until prospector is fixed to not break with the new pyroma release

Version 0.12.3
---------------
* `#190 <https://github.com/PyCQA/prospector/pull/190/>`_ Pinning pydocstyle version for now until API compatibility with newer versions can be written
* `#184 <https://github.com/PyCQA/prospector/pull/184/>`_ Including the LICENCE file when building dists
* Fixed a crash in the profile_validator tool if an empty profile was found
* (Version 0.12.2 does not exist due to a counting error...)

Version 0.12.1
---------------
* `#178 <https://github.com/PyCQA/prospector/pull/178/>`_ Long paths no longer cause crash in Windows.
* `#173 <https://github.com/PyCQA/prospector/issues/154/>`_ Changed from using pep8 to pycodestyle (which is what pep8 was renamed to)
* `#172 <https://github.com/PyCQA/prospector/issues/172/>`_ Fixed non-ascii file handling for mccabe tool and simplified all python source file reading

Version 0.12
---------------
* `#170 <https://github.com/PyCQA/prospector/issues/170/>`_ Changed from using pep257 to pydocstyle (which is what pep257 is now called)
* `#162 <https://github.com/PyCQA/prospector/issues/162/>`_ Properly warning about optional tools which are not installed
* `#166 <https://github.com/PyCQA/prospector/pulls/166/>`_ Added vscode formatter
* `#153 <https://github.com/PyCQA/prospector/pulls/153/>`_ Better pep257 support
* `#156 <https://github.com/PyCQA/prospector/pulls/156/>`_ Better pyroma logging hack for when pyroma is not installed
* `#158 <https://github.com/PyCQA/prospector/pulls/158/>`_ Fixed max-line-length command line option

Version 0.11.7
---------------
* Wrapping all tools so that none can directly write to stdout/stderr, as this breaks the output format for things like json. Instead, it is captured and optionally included as a regular message.

Version 0.11.6
---------------
* Yet more 'dodgy' encoding problem avoidance

Version 0.11.5
---------------
* Including forgotten 'python-targets' value in profile serialization

Version 0.11.4
---------------
* Prevented 'dodgy' tool from trying to analyse compressed text data

Version 0.11.3
---------------
* Fixed encoding of file contents handling by tool "dodgy" under Python3

Version 0.11.2
---------------
* Fixed a file encoding detection issue when running under Python3
* If a pylint plugin is specified in a .pylintrc file which cannot be loaded, prospector will now carry on with a warning rather than simply crash

Version 0.11.1
---------------
* `#147 <https://github.com/PyCQA/prospector/issues/147/>`_ Fixed crash when trying to load pylint configuration files in pylint 1.5

Version 0.11
---------------
* Compatibility fixes to work with pylint>=1.5
* McCabe tool now reports correct line and character number for syntax errors (and therefore gets blended if pylint etc detects such an error)
* Autodetect of libraries will now not search inside virtualenvironments
* `#142 <https://github.com/PyCQA/prospector/pull/142/>`_ better installation documentation in README (thanks `@ExcaliburZero <https://github.com/ExcaliburZero>`_)
* `#141 <https://github.com/PyCQA/prospector/issues/141/>`_ profile-validator no longer complains about member-warnings (thanks `@alefteris <https://github.com/alefteris>`_)
* `#140 <https://github.com/PyCQA/prospector/pull/140/>`_ emacs formatter includes character position (thanks `@philroberts <https://github.com/philroberts>`_)
* `#138 <https://github.com/PyCQA/prospector/pull/138/>`_ docs fixed for 'output-format' profile option (thanks `@faulkner <https://github.com/faulkner>`_)
* `#137 <https://github.com/PyCQA/prospector/pull/137/>`_ fixed various formatting issues in docs (thanks `@danstender <https://github.com/danstender>`_)
* `#132 <https://github.com/PyCQA/prospector/issues/132/>`_ Added support for custom flask linting thanks to the awesome [pylint-flask](https://github.com/jschaf/pylint-flask) plugin by [jschaf](https://github.com/jschaf)
* `#131 <https://github.com/PyCQA/prospector/pull/131/>`_, `#134 <https://github.com/PyCQA/prospector/pull/134/>`_ Custom pylint plugins are now loaded from existing .pylintrc files if present (thanks `@kaidokert <https://github.com/kaidokert>`_ and `@antoviaque <https://github.com/antoviaque>`_)

Version 0.10.2
---------------
* Added information to summary to explain what external configuration was used (if any) to configure the underlying tools
* Fixed supression-token search to use (or at least guess) correct file encoding

Version 0.10.1
---------------
* `#116 <https://github.com/PyCQA/prospector/issues/116/>`_ Comparison failed between messages with numeric values for character and those with a `None` value (thanks @smspillaz)
* `#118 <https://github.com/PyCQA/prospector/issues/118/>`_ Unified output of formatters to have correct output of str rather than bytes (thanks @prophile)
* `#115 <https://github.com/PyCQA/prospector/issues/115/>`_ Removed argparse as an explicit dependency as only Python 2.7+ is supported now

Version 0.10
---------------
* `#112 <https://github.com/PyCQA/prospector/issues/112/>`_ Profiles will now also be autoloaded from directories named `.prospector`.
* `#32 <https://github.com/PyCQA/prospector/issues/32/>`_ and `#108 <https://github.com/PyCQA/prospector/pull/108/>`_ Added a new 'xunit' output formatter for tools and services which integrate with this format (thanks to [lfrodrigues](https://github.com/lfrodrigues))
* Added a new built-in profile called 'flake8' for people who want to mimic the behaviour of 'flake8' using prospector.

Version 0.9.10
---------------
* The profile validator would load any file whose name was a subset of '.prospector.yaml' due to using the incorrect comparison operator.
* Fixing a crash when using an empty `ignore-patterns` list in a profile.
* Fixing a crash when a profile is not valid YAML at all.
* `#105 <https://github.com/PyCQA/prospector/pull/105/>`_ pyflakes was not correctly ignoring errors.

Version 0.9.9
---------------
* pep8.py 1.6.0 added new messages, which are now in prospector's built-in profiles

Version 0.9.8
---------------
* Fixing a crash when using pep8 1.6.0 due to the pep8 tool renaming something that Prospector uses

Version 0.9.7
---------------
* `#104 <https://github.com/PyCQA/prospector/issues/104/>`_ The previous attempt at normalising bytestrings and unicode in Python 2 was clumsily done and a bit broken. It is hopefully now using the correct voodoo incantations to get characters from one place to another.
* The blender combinations were not updated to use the new PyFlakes error codes; this is now fixed.

Version 0.9.6
---------------
* The profile validator tool was always outputting absolute paths in messages. This is now fixed.
* The "# NOQA" checking was using absolute paths incorrectly, which meant the message locations (with relative paths) did not match up and no messages were suppressed.

Version 0.9.5
---------------
* Fixed a problem with profile serialising where it was using the incorrect dict value for strictness

Version 0.9.4
---------------
* The previous PEP257 hack was not compatible with older versions of pep257.

Version 0.9.3
---------------
* The PEP257 tool sets a logging level of DEBUG globally when imported as of version 0.4.1, and this causes huge amounts of tokenzing debug to be output. Prospector now has a hacky workaround until that is fixed.
* Extra profile information (mainly the shorthand information) is kept when parsing and serializing profiles.

Version 0.9.2
---------------
* There were some problems related to absolute paths when loading profiles that were not in the current working directory.

Version 0.9.1
---------------
* Mandating version 0.2.3 of pylint-plugin-utils, as the earlier ones don't work with the add_message API changes made in pylint 1.4+

Version 0.9
---------------
* `#102 <https://github.com/PyCQA/prospector/pull/102/>`_ By default, prospector will hide pylint's "no-member" warnings, because more often than not they are simply incorrect. They can be re-enabled with the '--member-warnings' command line flag or the 'member-warnings: true' profile option.
* `#101 <https://github.com/PyCQA/prospector/pull/101/>`_ Code annotated with pep8/flake8 style "# noqa" comments is now understood by prospector and will lead to messages from other tools being suppressed too.
* `#100 <https://github.com/PyCQA/prospector/pull/100/>`_ Pyflakes error codes have been replaced with the same as those used in flake8, for consistency. Profiles with the old values will still work, and the profile-validator will warn you to upgrade.
* Messages now use Pylint error symbols ('star-args') instead of codes ('W0142'). This makes it much more obvious what each message means and what is happening when errors are suppressed or ignored in profiles. The old error codes will continue to work in profiles.
* The way that profiles are handled and parsed has completely been rewritten to avoid several bugs and introduce 'shorthand' options to profiles. This allows profiles to specify simple options like 'doc-warnings: true' inside profiles and configure anything that can be configured as a command line argument. Profiles can now use options like 'strictness: high' or 'doc-warnings: true' as a shortcut for inheriting the built-in prospector profiles.
* A new `--show-profile` option is available to dump the calculated profile, which is helpful for figuring out what prospector thinks it is doing.
* Profiles now have separate `ignore-paths` and `ignore-patterns` directives to match the command line arguments. The old `ignore` directive remains in place for backwards compatibility and will be deprecated in the future.
* A new tool, `profile-validator`, has been added. It simply checks prospector profiles and validates the settings, providing warnings if any are incorrect.
* `#89 <https://github.com/PyCQA/prospector/issues/89/>`_ and `#40 <https://github.com/PyCQA/prospector/pull/40/>`_ - profile merging was not behaving exactly as intended, with later profiles not overriding earlier profiles. This is now fixed as part of the aforementioned rewrite.
* pep257 is now included by default; however it will not run unless the '--doc-warnings' flag is used.
* pep257 messages are now properly blended with other tools' documentation warnings
* Path and output character encoding is now handled much better (which is to say, it is handled; previously it wasn't at all).

Version 0.8.3
---------------
* `#96 <https://github.com/PyCQA/prospector/issues/96/>`_ and `#97 <https://github.com/PyCQA/prospector/issues/97/>`_ - disabling messages in profiles now works for pep8

Version 0.8.2
---------------
* Version loading in setup.py no longer imports the prospector module (which could lead to various weirdnesses when installing on different platforms)
* `#82 <https://github.com/PyCQA/prospector/issues/82/>`_ resolves regression in adapter library detection raising, ``ValueError: too many values to unpack``. provided by `@jquast <https://github.com/jquast>`_
* `#83 <https://github.com/PyCQA/prospector/issues/83/>`_ resolves regression when adapter library detects django, ``TypeError: '_sre.SRE_Pattern' object is not iterable``. provided by `@jquast <https://github.com/jquast>`_

Version 0.8.1
---------------
* Strictness now also changes which pep257 messages are output
* pep257 and vulture messages are now combined and 'blended' with other tools
* `#80 <https://github.com/PyCQA/prospector/issues/80/>`_ Fix for Python3 issue when detecting libraries, provided by `@smspillaz <https://github.com/smspillaz>`_

Version 0.8
---------------
* Demoted frosted to be an optional tool - this is because development seems to have slowed and pyflakes has picked up again, and frosted how has several issues which are solved by pyflakes and is no longer a useful addition.
* `#78 <https://github.com/PyCQA/prospector/issues/78/>`_ Prospector can now take multiple files as a path argument, thus providing errors for several files at a time. This helps when integrating with IDEs, for example.
* Upgrading to newer versions of Pylint and related dependencies resolves `#73 <https://github.com/PyCQA/prospector/issues/73/>`_, `#75 <https://github.com/PyCQA/prospector/issues/75/>`_, `#76 <https://github.com/PyCQA/prospector/issues/76/>`_ and `#79 <https://github.com/PyCQA/prospector/issues/79/>`_
* `#74 <https://github.com/PyCQA/prospector/issues/74/>`_, `#10 <https://github.com/PyCQA/prospector/issues/10/>`_ Tools will now use any configuration specific to them by default. That is to say, if a `.pylintrc` file exists, then that will be used in preference to prospector's own opinions of how to use pylint.
* Added centralised configuration management, with an abstraction away from how prospector and each tool is actually configured.
* Removed the "adaptors" concept. This was a sort of visitor pattern in which each tool's configuration could be updated by an adaptor, which 'visited' the tool to tweak settings based on what the adaptor represented. In practise this was not useful and a confusing way to tweak behaviour - tools now configure themselves based on configuration options directly.
* Changed the default output format to be 'grouped' rather than 'text'
* Support for Python 2.6 has been dropped, following Pylint's lead.
* Using pylint 1.4's 'unsafe' mode, which allows it to load any C extensions (this was the behaviour for 1.3 and below). Not loading them causes many many inference errors.
* `#65 <https://github.com/PyCQA/prospector/issues/65/>`_ Resolve UnicodeDecodeErrors thrown while attempting to auto-discover modules of interest by discovering target python source file encoding (PEP263), and issuing only a warning if it fails (thanks to [Jeff Quast](https://github.com/jquast)).

Version 0.7.3
---------------
* Pylint dependency version restricted to 1.3, as 1.4 drops support for Python 2.6. Prospector will drop support for Python 2.6 in a 0.8 release.
* File names ending in 'tests.py' will now be ignored if prospector is set to ignore tests (previously, the regular expression only ignored files ending in 'test.py')
* `#70 <https://github.com/PyCQA/prospector/issues/70/>`_ Profiles starting with a `.yml` extension can now be autoloaded
* `#62 <https://github.com/PyCQA/prospector/issues/62/>`_ For human readable output, the summary of messages will now be printed at the end rather than at the start, so the summary will be what users see when running prospector (without piping into `less` etc)

Version 0.7.2
---------------
* The E265 error from PEP8 - "Block comment should start with '# '" - has been disabled for anything except veryhigh strictness.

Version 0.7.1
---------------
* `#60 <https://github.com/PyCQA/prospector/issues/60/>`_ Prospector did not work with Python2.6 due to timedelta.total_seconds() not being available.
* Restored the behaviour where std_out/std_err from pylint is suppressed

Version 0.7
---------------
* `#48 <https://github.com/PyCQA/prospector/issues/48/>`_ If a folder is detected to be a virtualenvironment, then prospector will not check the files inside.
* `#31 <https://github.com/PyCQA/prospector/issues/31/>`_ Prospector can now check single files if passed a module as the path argument.
* `#50 <https://github.com/PyCQA/prospector/issues/50/>`_ Prospector now uses an exit code of 1 to indicate that messages were found, to make it easier for bash scripts and so on to fail if any messages are found. A new flag, `-0` or `--zero-exit`, turns off this behaviour so that a non-zero exit code indicates that prospector failed to run.
* Profiles got an update to make them easier to understand and use. They are mostly the same as before, but `the documentation <http://prospector.readthedocs.org/en/latest/profiles.html>`_ and command line arguments have improved so that they can be reliably used.
* If a directive inline in code disables a pylint message, equivalent messages from other tools will now also be disabled.
* Added optional tools - additional tools which are not enabled by default but can be activated if the user chooses to.
* Added pyroma, a tool for validating packaging metadata, as an optional tool.
* `#29 <https://github.com/PyCQA/prospector/issues/29/>`_ Added support for pep257, a docstring format checker
* `#45 <https://github.com/PyCQA/prospector/issues/45/>`_ Added vulture, a tool for finding dead code, as an optional tool.
* `#24 <https://github.com/PyCQA/prospector/issues/24/>`_ Added Sphinx documentation, which is now also `available on ReadTheDocs <http://prospector.readthedocs.org/>`_

Version 0.6.4
---------------
* Fixed pylint system path munging again again

Version 0.6.3
---------------
* Fixed dodgy tool's use of new file finder

Version 0.6.2
---------------
* Fixed pylint system path munging again

Version 0.6.1
---------------
* Fixed pylint system path munging

Version 0.6
---------------
* Module and package finding has been centralised into a `finder.py` module, from which all tools take the list of files to be inspected. This helps unify which files get inspected, as previously there were several times when tools were not correctly ignoring files.
* Frosted [cannot handle non-utf-8 encoded files](https://github.com/timothycrosley/frosted/issues/56) so a workaround has been added to simply ignore encoding errors raised by Frosted until the bug is fixed. This was deemed okay as it is very similar to pyflakes in terms of what it finds, and pyflakes does not have this problem.
* `#43 <https://github.com/PyCQA/prospector/issues/43/>`_ - the blender is now smarter, and considers that a message may be part of more than one 'blend'. This means that some messages are no longer duplicated.
* `#42 <https://github.com/PyCQA/prospector/issues/42/>`_ - a few more message pairs were cleaned up, reducing ambiguity and redundancy
* `#33 <https://github.com/PyCQA/prospector/issues/33/>`_ - there is now an output format called `pylint` which mimics the pylint `--parseable` output format, with the slight difference that it includes the name of the tool as well as the code of the message.
* `#37 <https://github.com/PyCQA/prospector/issues/37/>`_ - profiles can now use the extension `.yml` as well as `.yaml`
* `#34 <https://github.com/PyCQA/prospector/issues/34/>`_ - south migrations are ignored if in the new south name of `south_migrations` (ie, this is compatible with the post-Django-1.7 world)

Version 0.5.6 / 0.5.5
---------------------
* The pylint path handling was slightly incorrect when multiple python modules were in the same directory and importing from each other, but no `__init__.py` package was present. If modules in such a directory imported from each other, pylint would crash, as the modules would not be in the `sys.path`. Note that 0.5.5 was released but this bugfix was not correctly merged before releasing. 0.5.6 contains this bugfix.

Version 0.5.4
---------------
* Fixing a bug in the handling of relative/absolute paths in the McCabe tool

Version 0.5.3
---------------
##### New Features

* Python 3.4 is now tested for and supported

##### Bug Fixes

* Module-level attributes can now be documented with a string without triggering a "String statement has no effect" warning
* `#28 <https://github.com/PyCQA/prospector/pull/28/>`_ Fixed absolute path bug with Frosted tool

Version 0.5.2
---------------
##### New Features

* Support for new error messages introduced in recent versions of `pep8` and `pylint` was included.

Version 0.5.1
---------------
##### New Features

* All command line arguments can now also be specified in a `tox.ini` and `setup.cfg` (thanks to [Jason Simeone](https://github.com/jayclassless))
* `--max-line-length` option can be used to override the maximum line length specified by the chosen strictness

##### Bug Fixes

* `#17 <https://github.com/PyCQA/prospector/issues/17/>`_ Prospector generates messages if in a path containing a directory beginning with a `.` - ignore patterns were previously incorrectly being applied to the absolute path rather than the relative path.
* `#12 <https://github.com/PyCQA/prospector/issues/12/>`_ Library support for Django now extends to all tools rather than just pylint
* Some additional bugs related to ignore paths were squashed.

Version 0.5
---------------
* Files and paths can now be ignored using the `--ignore-paths` and `--ignore-patterns` arguments.

* Full PEP8 compliance can be turned on using the `--full-pep8` flag, which overrides the defaults in the strictness profile.
* The PEP8 tool will now use existing config if any is found in `.pep8`, `tox.ini`, `setup.cfg` in the path to check, or `~/.config/pep8`. These will override any other configuration specified by Prospector. If none are present, Prospector will fall back on the defaults specified by the strictness.
* A new flag, `--external-config`, can be used to tweak how PEP8 treats external config. `only`, the default, means that external configuration will be preferred to Prospector configuration. `merge` means that Prospector will combine external configuration and its own values. `none` means that Prospector will ignore external config.

* The `--path` command line argument is no longer required, and Prospector can be called with `prospector path_to_check`.

* Pylint version 1.1 is now used.

* Prospector will now run under Python3.

Version 0.4.1
---------------
* Additional blending of messages - more messages indicating the same problem from different tools are now merged together
* Fixed the maximum line length to 160 for medium strictness, 100 for high and 80 for very high. This affects both the pep8 tool and pylint.

Version 0.4
---------------
* Added a changelog
* Added support for the `dodgy <https://github.com/landscapeio/dodgy>`_ codebase checker
* Added support for pep8 (thanks to `Jason Simeone <https://github.com/jayclassless>`_)
* Added support for pyflakes (thanks to `Jason Simeone <https://github.com/jayclassless>`_)
* Added support for mccabe (thanks to `Jason Simeone <https://github.com/jayclassless>`_)
* Replaced Pylint W0312 with a custom checker. This means that warnings are only generated for inconsistent indentation characters, rather than warning if spaces were not used.
* Some messages will now be combined if Pylint generates multiple warnings per line for what is the same cause. For example, 'unused import from wildcard import' messages are now combined rather than having one message per unused import from that line.
* Messages from multiple tools will be merged if they represent the same problem.
* Tool failure no longer kills the Prospector process but adds a message instead.
* Tools can be enabled or disabled from profiles.
* All style warnings can be suppressed using the ``--no-style-warnings`` command line switch.
* Uses a newer version of `pylint-django <https://github.com/landscapeio/pylint-django>`_ for improved analysis of Django-based code.
