# CrateDB

## Introduction

The Testcontainers module for [CrateDB](https://cratedb.com), a distributed SQL
database for real-time analytics. CrateDB is PostgreSQL wire-compatible and
provides a SQLAlchemy dialect (`crate://`) that talks to its HTTP interface.

## Adding this module to your project dependencies

Please run the following command to add the CrateDB module to your python dependencies:

```bash
pip install testcontainers[cratedb] sqlalchemy sqlalchemy-cratedb
```

## Usage example

<!--codeinclude-->

[Creating a CrateDB container](cratedb_example.py)

<!--/codeinclude-->

## Configuration

The CrateDB container can be configured with the following parameters:

- `image`: Docker image to use (default: `"crate/crate:latest"`)
- `port`: container port used to build the connection URL (default: `4200`, the HTTP interface)
- `username`: Database username (default: `"crate"`, or the `CRATEDB_USER` env var)
- `password`: Database password (default: `"crate"`, or the `CRATEDB_PASSWORD` env var)
- `dialect`: SQLAlchemy dialect used in the connection URL (default: `"crate"`)
- `cmd_opts`: extra `-C<key>=<value>` options passed to CrateDB (merged over the single-node defaults)
