Development and Contributing
============================

All contributions are very welcome! You can contribute in many ways:

* Join the `python code quality`_ mailing list and answer questions.

* Report bugs on the GitHub `issue tracker`_.

* Submit pull requests on the GitHub `repository`_. Ideally make a pull request to the *develop* branch, as I prefer to keep the master branch the same as the most recent release on PyPI. If you do this, be sure to add yourself to the CONTRIBUTORS.md file too!

.. _python code quality: https://mail.python.org/mailman/listinfo/code-quality
.. _issue tracker: https://github.com/landscapeio/prospector/issues
.. _repository: https://github.com/landscapeio/prospector


Tests
-----

There are not a huge number of tests right now, as most of the code in Prospector is
handling the output of other tools. However, please do run them before submitting a pull request::

    nosetests tests/

Prospector targets Python 2.6, 2.7, 3.3 and 3.4. You can use `tox`_ to test this locally,
and all tests are run on `travis.org`_.

.. _tox: https://tox.readthedocs.org/en/latest/
.. _travis.org: https://travis-ci.org/landscapeio/prospector
