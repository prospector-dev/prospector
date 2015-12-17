Prospector Changelog
=======
# Version 0.11.7
* Wrapping all tools so that none can directly write to stdout/stderr, as this breaks the output format for things like json. Instead, it is captured and optionally included as a regular message.

# Version 0.11.6
* Yet more 'dodgy' encoding problem avoidance

# Version 0.11.5
* Including forgotten 'python-targets' value in profile serialization

# Version 0.11.4
* Prevented 'dodgy' tool from trying to analyse compressed text data

# Version 0.11.3
* Fixed encoding of file contents handling by tool "dodgy" under Python3

## Version 0.11.2
* Fixed a file encoding detection issue when running under Python3
* If a pylint plugin is specified in a .pylintrc file which cannot be loaded, prospector will now carry on with a warning rather than simply crash

## Version 0.11.1
* [#147](https://github.com/landscapeio/prospector/issues/147) Fixed crash when trying to load pylint configuration files in pylint 1.5

## Version 0.11
* Compatability fixes to work with pylint>=1.5
* McCabe tool now reports correct line and character number for syntax errors (and therefore gets blended if pylint etc detects such an error)
* Autodetect of libraries will now not search inside virtualenvironments
* [#142](https://github.com/landscapeio/prospector/pull/142) better installation documentation in README (thanks [@ExcaliburZero](https://github.com/ExcaliburZero))
* [#141](https://github.com/landscapeio/prospector/issues/141) profile-validator no longer complains about member-warnings (thanks [@alefteris](https://github.com/alefteris))
* [#140](https://github.com/landscapeio/prospector/pull/140) emacs formatter includes character position (thanks [@philroberts](https://github.com/philroberts))
* [#138](https://github.com/landscapeio/prospector/pull/138) docs fixed for 'output-format' profile option (thanks [@faulkner](https://github.com/faulkner))
* [#137](https://github.com/landscapeio/prospector/pull/137) fixed various formatting issues in docs (thanks [@danstender](https://github.com/danstender))
* [#132](https://github.com/landscapeio/prospector/issues/132) Added support for custom flask linting thanks to the awesome [pylint-flask](https://github.com/jschaf/pylint-flask) plugin by [jschaf](https://github.com/jschaf)
* [#131](https://github.com/landscapeio/prospector/pull/131), [#134](https://github.com/landscapeio/prospector/pull/134) Custom pylint plugins are now loaded from existing .pylintrc files if present (thanks [@kaidokert](https://github.com/kaidokert) and [@antoviaque](https://github.com/antoviaque))

## Version 0.10.2
* Added information to summary to explain what external configuration was used (if any) to configure the underlying tools
* Fixed supression-token search to use (or at least guess) correct file encoding

## Version 0.10.1
* [#116](https://github.com/landscapeio/prospector/issues/116) Comparison failed between messages with numeric values for character and those with a `None` value (thanks @smspillaz)
* [#118](https://github.com/landscapeio/prospector/issues/118) Unified output of formatters to have correct output of str rather than bytes (thanks @prophile)
* [#115](https://github.com/landscapeio/prospector/issues/115) Removed argparse as an explicit dependency as only Python 2.7+ is supported now

## Version 0.10
* [#112](https://github.com/landscapeio/prospector/issues/112) Profiles will now also be autoloaded from directories named `.prospector`.
* [#32](https://github.com/landscapeio/prospector/issues/32) and [#108](https://github.com/landscapeio/prospector/pull/108) Added a new 'xunit' output formatter for tools and services which integrate with this format (thanks to [lfrodrigues](https://github.com/lfrodrigues))
* Added a new built-in profile called 'flake8' for people who want to mimic the behaviour of 'flake8' using prospector.

## Version 0.9.10
* The profile validator would load any file whose name was a subset of '.prospector.yaml' due to using the incorrect comparison operator.
* Fixing a crash when using an empty `ignore-patterns` list in a profile.
* Fixing a crash when a profile is not valid YAML at all.
* [#105](https://github.com/landscapeio/prospector/pull/105) pyflakes was not correctly ignoring errors.

## Version 0.9.9
* pep8.py 1.6.0 added new messages, which are now in prospector's built-in profiles

## Version 0.9.8
* Fixing a crash when using pep8 1.6.0 due to the pep8 tool renaming something that Prospector uses

## Version 0.9.7
* [#104](https://github.com/landscapeio/prospector/issues/104) The previous attempt at normalising bytestrings and unicode in Python 2 was clumsily done and a bit broken. It is hopefully now using the correct voodoo incantations to get characters from one place to another.
* The blender combinations were not updated to use the new PyFlakes error codes; this is now fixed.

## Version 0.9.6
* The profile validator tool was always outputting absolute paths in messages. This is now fixed.
* The "# NOQA" checking was using absolute paths incorrectly, which meant the message locations (with relative paths) did not match up and no messages were suppressed.

## Version 0.9.5
* Fixed a problem with profile serialising where it was using the incorrect dict value for strictness

## Version 0.9.4
* The previous PEP257 hack was not compatible with older versions of pep257.

## Version 0.9.3
* The PEP257 tool sets a logging level of DEBUG globally when imported as of version 0.4.1, and this causes huge amounts of tokenzing debug to be output. Prospector now has a hacky workaround until that is fixed.
* Extra profile information (mainly the shorthand information) is kept when parsing and serializing profiles.

## Version 0.9.2
* There were some problems related to absolute paths when loading profiles that were not in the current working directory.

## Version 0.9.1
* Mandating version 0.2.3 of pylint-plugin-utils, as the earlier ones don't work with the add_message API changes made in pylint 1.4+

## Version 0.9
* [#102](https://github.com/landscapeio/prospector/pull/102) By default, prospector will hide pylint's "no-member" warnings, because more often than not they are simply incorrect. They can be re-enabled with the '--member-warnings' command line flag or the 'member-warnings: true' profile option.
* [#101](https://github.com/landscapeio/prospector/pull/101) Code annotated with pep8/flake8 style "# noqa" comments is now understood by prospector and will lead to messages from other tools being suppressed too.
* [#100](https://github.com/landscapeio/prospector/pull/100) Pyflakes error codes have been replaced with the same as those used in flake8, for consistency. Profiles with the old values will still work, and the profile-validator will warn you to upgrade.
* Messages now use Pylint error symbols ('star-args') instead of codes ('W0142'). This makes it much more obvious what each message means and what is happening when errors are suppressed or ignored in profiles. The old error codes will continue to work in profiles.
* The way that profiles are handled and parsed has completely been rewritten to avoid several bugs and introduce 'shorthand' options to profiles. This allows profiles to specify simple options like 'doc-warnings: true' inside profiles and configure anything that can be configured as a command line argument. Profiles can now use options like 'strictness: high' or 'doc-warnings: true' as a shortcut for inheriting the built-in prospector profiles.
* A new `--show-profile` option is available to dump the calculated profile, which is helpful for figuring out what prospector thinks it is doing.
* Profiles now have separate `ignore-paths` and `ignore-patterns` directives to match the command line arguments. The old `ignore` directive remains in place for backwards compatibility and will be deprecated in the future.
* A new tool, `profile-validator`, has been added. It simply checks prospector profiles and validates the settings, providing warnings if any are incorrect.
* [#89](https://github.com/landscapeio/prospector/issues/89) and [#40](https://github.com/landscapeio/prospector/pull/40) - profile merging was not behaving exactly as intended, with later profiles not overriding earlier profiles. This is now fixed as part of the aforementioned rewrite.
* pep257 is now included by default; however it will not run unless the '--doc-warnings' flag is used.
* pep257 messages are now properly blended with other tools' documentation warnings
* Path and output character encoding is now handled much better (which is to say, it is handled; previously it wasn't at all).

## Version 0.8.3
* [#96](https://github.com/landscapeio/prospector/issues/96) and [#97](https://github.com/landscapeio/prospector/issues/97) - disabling messages in profiles now works for pep8

## Version 0.8.2
* Version loading in setup.py no longer imports the prospector module (which could lead to various weirdnesses when installing on different platforms)
* [#82](https://github.com/landscapeio/prospector/issues/82) resolves regression in adapter library detection raising, ``ValueError: too many values to unpack``. provided by [@jquast](https://github.com/jquast)
* [#83](https://github.com/landscapeio/prospector/issues/83) resolves regression when adapter library detects django, ``TypeError: '_sre.SRE_Pattern' object is not iterable``. provided by [@jquast](https://github.com/jquast)

## Version 0.8.1
* Strictness now also changes which pep257 messages are output
* pep257 and vulture messages are now combined and 'blended' with other tools
* [#80](https://github.com/landscapeio/prospector/issues/80) Fix for Python3 issue when detecting libraries, provided by [@smspillaz](https://github.com/smspillaz)

## Version 0.8
* Demoted frosted to be an optional tool - this is because development seems to have slowed and pyflakes has picked up again, and frosted how has several issues which are solved by pyflakes and is no longer a useful addition.
* [#78](https://github.com/landscapeio/prospector/issues/78) Prospector can now take multiple files as a path argument, thus providing errors for several files at a time. This helps when integrating with IDEs, for example.
* Upgrading to newer versions of Pylint and related dependencies resolves [#73](https://github.com/landscapeio/prospector/issues/73), [#75](https://github.com/landscapeio/prospector/issues/75), [#76](https://github.com/landscapeio/prospector/issues/76) and [#79](https://github.com/landscapeio/prospector/issues/79)
* [#74](https://github.com/landscapeio/prospector/issues/74), [#10](https://github.com/landscapeio/prospector/issues/10) Tools will now use any configuration specific to them by default. That is to say, if a `.pylintrc` file exists, then that will be used in preference to prospector's own opinions of how to use pylint.
* Added centralised configuration management, with an abstraction away from how prospector and each tool is actually configured.
* Removed the "adaptors" concept. This was a sort of visitor pattern in which each tool's configuration could be updated by an adaptor, which 'visited' the tool to tweak settings based on what the adaptor represented. In practise this was not useful and a confusing way to tweak behaviour - tools now configure themselves based on configuration options directly.
* Changed the default output format to be 'grouped' rather than 'text'
* Support for Python 2.6 has been dropped, following Pylint's lead.
* Using pylint 1.4's 'unsafe' mode, which allows it to load any C extensions (this was the behaviour for 1.3 and below). Not loading them causes many many inference errors.
* [#65](https://github.com/landscapeio/prospector/issues/65) Resolve UnicodeDecodeErrors thrown while attempting to auto-discover modules of interest by discovering target python source file encoding (PEP263), and issuing only a warning if it fails (thanks to [Jeff Quast](https://github.com/jquast)).

## Version 0.7.3

* Pylint dependency version restricted to 1.3, as 1.4 drops support for Python 2.6. Prospector will drop support for Python 2.6 in a 0.8 release.
* File names ending in 'tests.py' will now be ignored if prospector is set to ignore tests (previously, the regular expression only ignored files ending in 'test.py')
* [#70](https://github.com/landscapeio/prospector/issues/70) Profiles starting with a `.yml` extension can now be autoloaded
* [#62](https://github.com/landscapeio/prospector/issues/62) For human readable output, the summary of messages will now be printed at the end rather than at the start, so the summary will be what users see when running prospector (without piping into `less` etc)

## Version 0.7.2

* The E265 error from PEP8 - "Block comment should start with '# '" - has been disabled for anything except veryhigh strictness.

## Version 0.7.1

* [#60](https://github.com/landscapeio/prospector/issues/60) Prospector did not work with Python2.6 due to timedelta.total_seconds() not being available.
* Restored the behaviour where std_out/std_err from pylint is suppressed

## Version 0.7

* [#48](https://github.com/landscapeio/prospector/issues/48) If a folder is detected to be a virtualenvironment, then prospector will not check the files inside.
* [#31](https://github.com/landscapeio/prospector/issues/31) Prospector can now check single files if passed a module as the path argument.
* [#50](https://github.com/landscapeio/prospector/issues/50) Prospector now uses an exit code of 1 to indicate that messages were found, to make it easier for bash scripts and so on to fail if any messages are found. A new flag, `-0` or `--zero-exit`, turns off this behaviour so that a non-zero exit code indicates that prospector failed to run.
* Profiles got an update to make them easier to understand and use. They are mostly the same as before, but [the documentation](http://prospector.readthedocs.org/en/latest/profiles.html) and command line arguments have improved so that they can be reliably used.
* If a directive inline in code disables a pylint message, equivalent messages from other tools will now also be disabled.
* Added optional tools - additional tools which are not enabled by default but can be activated if the user chooses to.
* Added pyroma, a tool for validating packaging metadata, as an optional tool.
* [#29](https://github.com/landscapeio/prospector/issues/29) Added support for pep257, a docstring format checker
* [#45](https://github.com/landscapeio/prospector/issues/45) Added vulture, a tool for finding dead code, as an optional tool.
* [#24](https://github.com/landscapeio/prospector/issues/24) Added Sphinx documentation, which is now also [available on ReadTheDocs](http://prospector.readthedocs.org/)

## Version 0.6.4

* Fixed pylint system path munging again again

## Version 0.6.3

* Fixed dodgy tool's use of new file finder

## Version 0.6.2

* Fixed pylint system path munging again

## Version 0.6.1

* Fixed pylint system path munging

## Version 0.6

* Module and package finding has been centralised into a `finder.py` module, from which all tools take the list of files to be inspected. This helps unify which files get inspected, as previously there were several times when tools were not correctly ignoring files.
* Frosted [cannot handle non-utf-8 encoded files](https://github.com/timothycrosley/frosted/issues/56) so a workaround has been added to simply ignore encoding errors raised by Frosted until the bug is fixed. This was deemed okay as it is very similar to pyflakes in terms of what it finds, and pyflakes does not have this problem.
* [#43](https://github.com/landscapeio/prospector/issues/43) - the blender is now smarter, and considers that a message may be part of more than one 'blend'. This means that some messages are no longer duplicated.
* [#42](https://github.com/landscapeio/prospector/issues/42) - a few more message pairs were cleaned up, reducing ambiguity and redundancy
* [#33](https://github.com/landscapeio/prospector/issues/33) - there is now an output format called `pylint` which mimics the pylint `--parseable` output format, with the slight difference that it includes the name of the tool as well as the code of the message.
* [#37](https://github.com/landscapeio/prospector/issues/37) - profiles can now use the extension `.yml` as well as `.yaml`
* [#34](https://github.com/landscapeio/prospector/issues/34) - south migrations are ignored if in the new south name of `south_migrations` (ie, this is compatible with the post-Django-1.7 world)

## Version 0.5.6 / 0.5.5

* The pylint path handling was slightly incorrect when multiple python modules were in the same directory and importing from each other, but no `__init__.py` package was present. If modules in such a directory imported from each other, pylint would crash, as the modules would not be in the `sys.path`. Note that 0.5.5 was released but this bugfix was not correctly merged before releasing. 0.5.6 contains this bugfix.

## Version 0.5.4

* Fixing a bug in the handling of relative/absolute paths in the McCabe tool

## Version 0.5.3

##### New Features

* Python 3.4 is now tested for and supported

##### Bug Fixes

* Module-level attributes can now be documented with a string without triggering a "String statement has no effect" warning
* [#28](https://github.com/landscapeio/prospector/pull/28) Fixed absolute path bug with Frosted tool

## Version 0.5.2

##### New Features

* Support for new error messages introduced in recent versions of `pep8` and `pylint` was included.

## Version 0.5.1

##### New Features

* All command line arguments can now also be specified in a `tox.ini` and `setup.cfg` (thanks to [Jason Simeone](https://github.com/jayclassless))
* `--max-line-length` option can be used to override the maximum line length specified by the chosen strictness

##### Bug Fixes

* [#17](https://github.com/landscapeio/prospector/issues/17) Prospector generates messages if in a path containing a directory beginning with a `.` - ignore patterns were previously incorrectly being applied to the absolute path rather than the relative path.
* [#12](https://github.com/landscapeio/prospector/issues/12) Library support for Django now extends to all tools rather than just pylint
* Some additional bugs related to ignore paths were squashed.

## Version 0.5

* Files and paths can now be ignored using the `--ignore-paths` and `--ignore-patterns` arguments.

* Full PEP8 compliance can be turned on using the `--full-pep8` flag, which overrides the defaults in the strictness profile.
* The PEP8 tool will now use existing config if any is found in `.pep8`, `tox.ini`, `setup.cfg` in the path to check, or `~/.config/pep8`. These will override any other configuration specified by Prospector. If none are present, Prospector will fall back on the defaults specified by the strictness.
* A new flag, `--external-config`, can be used to tweak how PEP8 treats external config. `only`, the default, means that external configuration will be preferred to Prospector configuration. `merge` means that Prospector will combine external configuration and its own
values. `none` means that Prospector will ignore external config.

* The `--path` command line argument is no longer required, and Prospector can be called with `prospector path_to_check`.

* Pylint version 1.1 is now used.

* Prospector will now run under Python3.

## Version 0.4.1

* Additional blending of messages - more messages indicating the same problem from different tools are now merged together
* Fixed the maximum line length to 160 for medium strictness, 100 for high and 80 for very high. This affects both the pep8 tool and pylint.

## Version 0.4

* Added a changelog
* Added support for the [dodgy](https://github.com/landscapeio/dodgy) codebase checker
* Added support for pep8 (thanks to [Jason Simeone](https://github.com/jayclassless))
* Added support for pyflakes (thanks to [Jason Simeone](https://github.com/jayclassless))
* Added support for mccabe (thanks to [Jason Simeone](https://github.com/jayclassless))
* Replaced Pylint W0312 with a custom checker. This means that warnings are only generated for inconsistent indentation characters, rather than warning if spaces were not used.
* Some messages will now be combined if Pylint generates multiple warnings per line for what is the same cause. For example, 'unused import from wildcard import' messages are now combined rather than having one message per unused import from that line.
* Messages from multiple tools will be merged if they represent the same problem.
* Tool failure no longer kills the Prospector process but adds a message instead.
* Tools can be enabled or disabled from profiles.
* All style warnings can be suppressed using the `--no-style-warnings` command line switch.
* Uses a newer version of [pylint-django](https://github.com/landscapeio/pylint-django) for improved analysis of Django-based code.
