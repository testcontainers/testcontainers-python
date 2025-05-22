# CockroachDB

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.7.0"><span class="tc-version">:material-tag: v4.7.0</span></a>

## Introduction

The Testcontainers module for CockroachDB.

## Adding this module to your project dependencies

Please run the following command to add the CockroachDB module to your python dependencies:

```bash
pip install testcontainers[cockroachdb] sqlalchemy psycopg2
```

## Usage example

<!--codeinclude-->

[Creating a CockroachDB container](../../modules/cockroachdb/example_basic.py)

<!--/codeinclude-->

## Features

- Distributed SQL database
- ACID transactions
- Strong consistency
- Horizontal scaling
- Built-in replication
- Automatic sharding
- SQL compatibility
- Integration with pandas for data analysis

## Configuration

The CockroachDB container can be configured with the following parameters:

- `username`: Database username (default: "root")
- `password`: Database password (default: "")
- `database`: Database name (default: "postgres")
- `port`: Port to expose (default: 26257)
- `version`: CockroachDB version to use (default: "latest")
