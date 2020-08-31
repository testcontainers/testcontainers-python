testcontainers-python
=====================

.. image:: https://travis-ci.org/testcontainers/testcontainers-python.svg?branch=master
   :target: https://travis-ci.org/testcontainers/testcontainers-python
.. image:: https://img.shields.io/pypi/v/testcontainers.svg?style=flat-square
   :target: https://pypi.python.org/pypi/testcontainers
.. image:: https://readthedocs.org/projects/testcontainers-python/badge/?version=latest
   :target: http://testcontainers-python.readthedocs.io/en/latest/?badge=latest

Python port for testcontainers-java that allows using docker containers for functional and integration testing. Testcontainers-python provides capabilities to spin up docker containers (such as a database, Selenium web browser, or any other container) for testing.

Currently available features:

* Selenium Grid containers
* Selenium Standalone containers
* MySql Db container
* MariaDb container
* Neo4j container
* OracleDb container
* PostgreSQL Db container
* Microsoft SQL Server container
* Generic docker containers
* LocalStack

Installation
------------

The testcontainers package is available from `PyPI <https://pypi.org/project/testcontainers/>`_, and it can be installed using :code:`pip`. Depending on which containers are needed, you can specify additional dependencies as `extras <https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`_:

.. code-block:: bash

    # Install without extras
    pip install testcontainers
    # Install with one or more extras
    pip install testcontainers[mysql]
    pip install testcontainers[mysql,oracle]

Basic usage
-----------

.. code-block:: python

    import sqlalchemy
    from testcontainers.mysql import MySqlContainer

    with MySqlContainer('mysql:5.7.17') as mysql:
        engine = sqlalchemy.create_engine(mysql.get_connection_url())
        version, = engine.execute("select version()").fetchone()
        print(version)  # 5.7.17

The snippet above will spin up a MySql database in a container. The :code:`get_connection_url()` convenience method returns a :code:`sqlalchemy` compatible url we use to connect to the database and retrieve the database version.

More extensive documentation can be found at `Read The Docs <http://testcontainers-python.readthedocs.io/>`_.

Usage within Docker (i.e. in a CI)
----------------------------------

When trying to launch a testcontainer from within a Docker container two things have to be provided:

1. The container has to provide a docker client installation. Either use an image that has docker pre-installed (e.g. the [official docker images](https://hub.docker.com/_/docker)) or install the client from within the `Dockerfile` specification.
2. The container has to have access to the docker daemon which can be achieved by mounting `/var/run/docker.sock` or setting the `DOCKER_HOST` environment variable as part of your `docker run` command.


Setting up a development environment
------------------------------------

We recommend you use a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for development. Note that a python version :code:`>=3.5` is required. After setting up your virtual environment, you can install all dependencies and test the installation by running the following snippet.

.. code-block:: bash

    pip install -r requirements/$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])').txt
    pytest -s

Adding requirements
^^^^^^^^^^^^^^^^^^^

We use :code:`pip-tools` to resolve and manage dependencies. If you need to add a dependency to testcontainers or one of the extras, run :code:`pip install pip-tools` followed by :code:`make requirements` to update the requirements files.
