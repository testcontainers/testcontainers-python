# testcontainers-python

[![Build Status](https://travis-ci.org/testcontainers/testcontainers-python.svg?branch=master)](https://travis-ci.org/testcontainers/testcontainers-python) [![PyPI](https://img.shields.io/pypi/v/testcontainers.svg?style=flat-square)](https://pypi.python.org/pypi/testcontainers)
[![Documentation Status](https://readthedocs.org/projects/testcontainers-python/badge/?version=latest)](http://testcontainers-python.readthedocs.io/en/latest/?badge=latest)

Python port for testcontainers-java that allows using docker containers for functional and/or integration testing. Testcontainers-python provides capabilities to spin up a docker containers for test purposes would that be a database, Selenium web browser, or any other container.

Currently available features:

* Selenium Grid containers
* Selenium Standalone containers
* MySql Db container
* MariaDb container
* OracleDb container
* PostgreSQL Db container
* Microsoft SQL Server container
* Generic docker containers

## Installation

The testcontainers package is available from [PyPI](https://pypi.org/project/testcontainers/), and it can be installed using ``pip``. Depending on which containers are needed, you can specify additional dependencies as [extras](https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies):

```bash
# Install without extras
pip install testcontainers
# Install with one or more extras
pip install testcontainers[mysql]
pip install testcontainers[mysql,oracle]
```

## Basic usage

```python
import sqlalchemy
from testcontainers.mysql import MySqlContainer

with MySqlContainer('mysql:5.7.17') as mysql:
    engine = sqlalchemy.create_engine(mysql.get_connection_url())
    version, = engine.execute("select version()").fetchone()
    print(version)  # 5.7.17
```

The snippet above will spin up a MySql database in a container. The `get_connection_url()` convenience method returns a `sqlalchemy` compatible url we use to connect to the database and retrieve the database version.

More extensive documentation can be found at [Read The Docs](http://testcontainers-python.readthedocs.io/).

## Setting up a development environment

We recommend you use a [virtual environment](https://virtualenv.pypa.io/en/stable/) for development. Note that a python version `>=3.5` is required. After setting up your virtual environment, you can install all dependencies and test the installation by running the following snippet.

```bash
pip install -r requirements/$(python -c 'import sys; print("%d.%d" % sys.version_info[:2])').txt
pytest -s
```

### Adding requirements

We use `pip-tools` to resolve and manage dependencies. If you need to add a dependency to testcontainers or one of the extras, run `pip install pip-tools` followed by `make requirements` to update the requirements files.
