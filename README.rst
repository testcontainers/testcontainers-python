testcontainers-python
=====================

.. image:: https://github.com/testcontainers/testcontainers-python/workflows/testcontainers-python/badge.svg
   :target: https://github.com/testcontainers/testcontainers-python/actions/workflows/main.yml
.. image:: https://img.shields.io/pypi/v/testcontainers.svg
   :target: https://pypi.python.org/pypi/testcontainers
.. image:: https://readthedocs.org/projects/testcontainers-python/badge/?version=latest
   :target: http://testcontainers-python.readthedocs.io/en/latest/?badge=latest

testcontainers-python facilitates the use of Docker containers for functional and integration testing. The collection of packages currently supports the following features.

.. toctree::

    core/README
    arangodb/README
    azurite/README
    clickhouse/README
    compose/README
    elasticsearch/README
    google/README
    kafka/README
    keycloak/README
    localstack/README
    minio/README
    mongodb/README
    mssql/README
    mysql/README
    neo4j/README
    nginx/README
    opensearch/README
    oracle/README
    postgres/README
    rabbitmq/README
    redis/README
    selenium/README

Getting Started
---------------

.. doctest::

    >>> from testcontainers.postgres import PostgresContainer
    >>> import sqlalchemy

    >>> with PostgresContainer("postgres:9.5") as postgres:
    ...     engine = sqlalchemy.create_engine(postgres.get_connection_url())
    ...     result = engine.execute("select version()")
    ...     version, = result.fetchone()
    >>> version
    'PostgreSQL 9.5...'

The snippet above will spin up a postgres database in a container. The :code:`get_connection_url()` convenience method returns a :code:`sqlalchemy` compatible url we use to connect to the database and retrieve the database version.

Installation
------------

The suite of testcontainers packages is available on `PyPI <https://pypi.org/project/testcontainers/>`_, and individual packages can be installed using :code:`pip`. We recommend installing the package you need by running :code:`pip install testcontainers-<feature>`, e.g., :code:`pip install testcontainers-postgres`.

.. note::

    For backwards compatibility, packages can also be installed by specifying `extras <https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`__, e.g., :code:`pip install testcontainers[postgres]`.


Docker in Docker (DinD)
-----------------------

When trying to launch a testcontainer from within a Docker container, e.g., in continuous integration testing, two things have to be provided:

1. The container has to provide a docker client installation. Either use an image that has docker pre-installed (e.g. the `official docker images <https://hub.docker.com/_/docker>`_) or install the client from within the `Dockerfile` specification.
2. The container has to have access to the docker daemon which can be achieved by mounting `/var/run/docker.sock` or setting the `DOCKER_HOST` environment variable as part of your `docker run` command.

Development and Contributing
----------------------------

We recommend you use a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for development (:code:`python>=3.7` is required). After setting up your virtual environment, you can install all dependencies and test the installation by running the following snippet.

.. code-block:: bash

    pip install -r requirements/[your python version].txt
    pytest -s

Package Structure
^^^^^^^^^^^^^^^^^

Testcontainers is a collection of `implicit namespace packages <https://peps.python.org/pep-0420/>`__ to decouple the development of different extensions, e.g., :code:`testcontainers-mysql` and :code:`testcontainers-postgres` for MySQL and PostgreSQL database containers, respectively. The folder structure is as follows.

.. code-block:: bash

    # One folder per feature.
    [feature name]
        # Folder without __init__.py for implicit namespace packages.
        testcontainers
            # Implementation as namespace package with __init__.py.
            [feature name]
                __init__.py
                # Other files for this
                ...
        # Tests for the feature.
        tests
            test_[feature_name].py
            ...
        # README for this feature.
        README.rst
        # Setup script for this feature.
        setup.py

Contributing a New Feature
^^^^^^^^^^^^^^^^^^^^^^^^^^

You want to contribute a new feature or container? Great! You can do that in six steps.

1. Create a new feature directory and populate it with the [package structure]_ as described above. Copying one of the existing features is likely the best way to get started.
2. Implement the new feature (typically in :code:`__init__.py`) and corresponding tests.
3. Add a line :code:`-e file:[feature name]` to :code:`requirements.in` and run :code:`make requirements`. This command will find any new requirements and generate lock files to ensure reproducible builds (see the `pip-tools <https://pip-tools.readthedocs.io/en/latest/>`__ documentation for details). Then run :code:`pip install -r requirements/[your python version].txt` to install the new requirements.
4. Update the feature :code:`README.rst` and add it to the table of contents (:code:`toctree` directive) in the top-level :code:`README.rst`.
5. Add a line :code:`[feature name]` to the list of components in the  GitHub Action workflow in :code:`.github/workflows/main.yml` to run tests, build, and publish your package when pushed to the :code:`master` branch.
6. Rebase your development branch on :code:`master` (or merge :code:`master` into your development branch).
