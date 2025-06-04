# DB2

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.8.0"><span class="tc-version">:material-tag: v4.8.0</span></a>

## Introduction

The Testcontainers module for IBM Db2.

## Adding this module to your project dependencies

Please run the following command to add the DB2 module to your python dependencies:

```bash
pip install testcontainers[db2] sqlalchemy ibm-db
```

## Usage example

<!--codeinclude-->

[Creating a DB2 container](../../modules/db2/example_basic.py)

<!--/codeinclude-->

## Features

- Full SQL support
- Transaction management
- Stored procedures
- User-defined functions
- Advanced analytics
- JSON support
- Integration with pandas for data analysis

## Configuration

The DB2 container can be configured with the following parameters:

- `username`: Database username (default: "db2inst1")
- `password`: Database password (default: "password")
- `database`: Database name (default: "testdb")
- `port`: Port to expose (default: 50000)
- `version`: DB2 version to use (default: "latest")
