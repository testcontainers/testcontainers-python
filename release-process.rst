Release process
===============

Run tests on target branch
--------------------------

Steps::

    tox -epep8
    tox -esphinx-docs


Declare package version
------------------------

In setup.py bump version to the next::

    version='X.X.X'  to version='X.X.Y'

Cut off stable branch
---------------------

Steps::

    git checkout -b vX.X.X-stable
    git push origin vX.X.X-stable


Create GitHub tag
-----------------

Steps::

    Releases ---> Draft New Release
    Name: python-testrelease version X.X.X stable release


Collect changes from previous version
-------------------------------------

Steps::

    git log --oneline --decorate


Build distribution package
--------------------------

Steps::

    python setup.py bdist_wheel


Check install capability for the wheel
--------------------------------------

Steps::

    virtualenv .test_venv
    source .test_venv/bin/activate
    pip install dist/testcontainer-X.X.X-py2.py3-none-any.whl


Submit release to PYPI
----------------------

Steps::

    twine dist/* upload
