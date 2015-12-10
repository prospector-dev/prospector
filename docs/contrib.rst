Development and Contributing
============================

All contributions are very welcome! You can contribute in many ways:

* Join the `python code quality`_ mailing list and answer questions.

* Report bugs on the GitHub `issue tracker`_.

* Submit pull requests on the GitHub `repository`_. Ideally make a pull request to the *develop* branch, as I prefer to keep the master branch the same as the most recent release on PyPI. If you do this, be sure to add yourself to the CONTRIBUTORS.md file too!

.. _python code quality: https://mail.python.org/mailman/listinfo/code-quality
.. _issue tracker: https://github.com/landscapeio/prospector/issues
.. _repository: https://github.com/landscapeio/prospector


Code Quality
------------

As a code quality testing tool, it makes sense to strive to be a good example of good code!
To that end, prospector is checked by `Landscape <https://landscape.io>_` and ideally when
making a pull request, please take note of any decreases in quality.

Additionally, there is a `pre-commit <http://pre-commit.com/>`_ configuration to prevent
various small problems before they are committed. Check the site for more information but
the short version is::

    pip install pre-commit
    pre-commit install


Tests
-----

There are not a huge number of tests right now, as most of the code in Prospector is
handling the output of other tools. However, please do run them before submitting a pull request::

    nosetests tests/

Prospector targets Python 2.7, 3.3 and 3.4. You can use `tox`_ to test this locally,
and all tests are run on `travis.org`_.

.. _tox: https://tox.readthedocs.org/en/latest/
.. _travis.org: https://travis-ci.org/landscapeio/prospector
