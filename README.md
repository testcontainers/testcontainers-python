# testcontainers-python

[![Build Status](https://travis-ci.org/testcontainers/testcontainers-python.svg?branch=master)](https://travis-ci.org/testcontainers/testcontainers-python) [![PyPI](https://img.shields.io/pypi/v/testcontainers.svg?style=flat-square)](https://pypi.python.org/pypi/testcontainers)
[![Documentation Status](https://readthedocs.org/projects/testcontainers-python/badge/?version=latest)](http://testcontainers-python.readthedocs.io/en/latest/?badge=latest)

Python port for testcontainers-java that allows using docker containers for functional and/or integration testing.

Testcontainers-python provides capabilities to spin up a docker containers for test purposes would that be a database, Selenium web browser or any other cotainer.

Currently available features:

* Selenium Grid containers
* Selenium Standalone containers
* MySql Db container
* MariaDb container
* OracleDb container
* PostgreSQL Db container
* Generic docker containers

### Quick start

Installation
------------

The **testcontainers** module is available from PyPI at:

* https://pypi.python.org/pypi/testcontainers

and can be installed using ``pip``, depending on which containers you need:

    pip install testcontainers[mysql]
    pip install testcontainers[oracle]
    pip install testcontainers[postgresql]
    pip install testcontainers[selenium]
    # or with multiple
    pip install testcontainers[mysql,postgresql,selenium]

Basic usage
-----------

Database containers

Allows to spin up docker database images such as MySQL, PostgreSQL, MariaDB and Oracle XE.

MySQL example
-------------

        config = MySqlContainer('mysql:5.7.17')
        with config as mysql:
            e = sqlalchemy.create_engine(mysql.get_connection_url())
            result = e.execute("select version()")

It will spin up MySQL version 5.7. Then you can connect to database using ``get_connection_url()`` method which returns sqlalchemy compatible url in format ``dialect+driver://username:password@host:port/database``.

# Detailed [documentation](http://testcontainers-python.readthedocs.io/en/latest/)
