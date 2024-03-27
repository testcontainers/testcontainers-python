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

## Configuration

| Env Variable                            | Example                     | Description                                                                        |
| --------------------------------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE` | `/var/run/docker.sock`      | Path to Docker's socket used by ryuk                                               |
| `TESTCONTAINERS_RYUK_PRIVILEGED`        | `false`                     | Run ryuk as a privileged container                                                 |
| `TESTCONTAINERS_RYUK_DISABLED`          | `false`                     | Disable ryuk                                                                       |
| `RYUK_CONTAINER_IMAGE`                  | `testcontainers/ryuk:0.7.0` | Custom image for ryuk                                                              |
| `RYUK_RECONNECTION_TIMEOUT`             | `10s`                       | Reconnection timeout for Ryuk TCP socket before Ryuk reaps all dangling containers |
