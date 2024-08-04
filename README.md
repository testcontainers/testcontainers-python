[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![PyPI - Version](https://img.shields.io/pypi/v/testcontainers)
[![PyPI - License](https://img.shields.io/pypi/l/testcontainers.svg)](https://github.com/testcontainers/testcontainers-python/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/testcontainers.svg)](https://pypi.python.org/pypi/testcontainers)
[![codecov](https://codecov.io/gh/testcontainers/testcontainers-python/branch/master/graph/badge.svg)](https://codecov.io/gh/testcontainers/testcontainers-python)
![Core Tests](https://github.com/testcontainers/testcontainers-python/actions/workflows/ci-core.yml/badge.svg)
![Community Tests](https://github.com/testcontainers/testcontainers-python/actions/workflows/ci-community.yml/badge.svg)
[![Docs](https://readthedocs.org/projects/testcontainers-python/badge/?version=latest)](http://testcontainers-python.readthedocs.io/en/latest/?badge=latest)

[![Codespace](https://github.com/codespaces/badge.svg)](https://codespaces.new/testcontainers/testcontainers-python)

# Testcontainers Python

`testcontainers-python` facilitates the use of Docker containers for functional and integration testing.

For more information, see [the docs][readthedocs].

[readthedocs]: https://testcontainers-python.readthedocs.io/en/latest/

## Getting Started

```pycon
>>> from testcontainers.postgres import PostgresContainer
>>> import sqlalchemy

>>> with PostgresContainer("postgres:16") as postgres:
...     engine = sqlalchemy.create_engine(postgres.get_connection_url())
...     with engine.begin() as connection:
...         result = connection.execute(sqlalchemy.text("select version()"))
...         version, = result.fetchone()
>>> version
'PostgreSQL 16...'
```

The snippet above will spin up a postgres database in a container. The `get_connection_url()` convenience method returns a `sqlalchemy` compatible url we use to connect to the database and retrieve the database version.

## Contributing / Development / Release

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for more details.

## Configuration

| Env Variable                            | Example                     | Description                                                                        |
| --------------------------------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE` | `/var/run/docker.sock`      | Path to Docker's socket used by ryuk                                               |
| `TESTCONTAINERS_RYUK_PRIVILEGED`        | `false`                     | Run ryuk as a privileged container                                                 |
| `TESTCONTAINERS_RYUK_DISABLED`          | `false`                     | Disable ryuk                                                                       |
| `RYUK_CONTAINER_IMAGE`                  | `testcontainers/ryuk:0.8.1` | Custom image for ryuk                                                              |
| `RYUK_RECONNECTION_TIMEOUT`             | `10s`                       | Reconnection timeout for Ryuk TCP socket before Ryuk reaps all dangling containers |
