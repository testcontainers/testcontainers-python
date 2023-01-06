testcontainers-python
=====================

.. image:: https://github.com/testcontainers/testcontainers-python/workflows/testcontainers-python/badge.svg
   :target: https://github.com/testcontainers/testcontainers-python/actions/workflows/main.yml
.. image:: https://img.shields.io/pypi/v/testcontainers.svg?style=flat-square
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

Basic usage
-----------

.. doctest::

    >>> from testcontainers.postgres import PostgresContainer
    >>> import sqlalchemy

    >>> postgres_container = PostgresContainer("postgres:9.5")
    >>> with postgres_container as postgres:
    ...     e = sqlalchemy.create_engine(postgres.get_connection_url())
    ...     result = e.execute("select version()")
    ...     version, = result.fetchone()
    >>> version
    'PostgreSQL 9.5...'

The snippet above will spin up a postgres database in a container. The :code:`get_connection_url()` convenience method returns a :code:`sqlalchemy` compatible url we use to connect to the database and retrieve the database version. More extensive documentation can be found at `Read The Docs <http://testcontainers-python.readthedocs.io/>`_.

Installation
------------

The suite of testcontainers packages is available on `PyPI <https://pypi.org/project/testcontainers/>`_, and individual packages can be installed using :code:`pip`. We recommend installing the package you need by running :code:`pip install testcontainers-<feature>`, e.g., :code:`pip install testcontainers-mysql`.

For backwards compatibility, packages can also be installed by specifying `extras <https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`__, e.g., :code:`pip install testcontainers[mysql]`.


Usage within Docker (e.g., in a CI)
-----------------------------------

When trying to launch a testcontainer from within a Docker container two things have to be provided:

1. The container has to provide a docker client installation. Either use an image that has docker pre-installed (e.g. the `official docker images <https://hub.docker.com/_/docker>`_) or install the client from within the `Dockerfile` specification.
2. The container has to have access to the docker daemon which can be achieved by mounting `/var/run/docker.sock` or setting the `DOCKER_HOST` environment variable as part of your `docker run` command.

Setting up a development environment
------------------------------------

We recommend you use a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for development. Note that a python version :code:`>=3.7` is required. After setting up your virtual environment, you can install all dependencies and test the installation by running the following snippet.

.. code-block:: bash

    pip install -r requirements/$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])').txt
    pytest -s

Adding requirements
^^^^^^^^^^^^^^^^^^^

We use :code:`pip-tools` to resolve and manage dependencies. If you need to add a dependency to testcontainers or one of the extras, modify the :code:`setup.py` as well as the :code:`requirements.in` accordingly and then run :code:`pip install pip-tools` followed by :code:`make requirements` to update the requirements files.

Contributing a new container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can contribute a new container in three steps:

1. Create a new module at :code:`testcontainers/[my fancy container].py` that implements the new functionality.
2. Create a new test module at :code:`tests/test_[my fancy container].py` that tests the new functionality.
3. Add :code:`[my fancy container]` to the list of test components in the GitHub Action configuration at :code:`.github/workflows/main.yml`.
