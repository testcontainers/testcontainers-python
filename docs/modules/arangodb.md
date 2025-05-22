# ArangoDB

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.6.0"><span class="tc-version">:material-tag: v4.6.0</span></a>

## Introduction

The Testcontainers module for ArangoDB.

## Adding this module to your project dependencies

Please run the following command to add the ArangoDB module to your python dependencies:

```bash
pip install testcontainers[arangodb] python-arango
```

## Usage example

<!--codeinclude-->

[Creating an ArangoDB container](../../modules/arangodb/example_basic.py)

<!--/codeinclude-->

## Features

- Multi-model database support (key-value, document, graph)
- AQL (ArangoDB Query Language) for complex queries
- Built-in aggregation functions
- Collection management
- Document CRUD operations
- Bulk document import

## Configuration

The ArangoDB container can be configured with the following parameters:

- `username`: Database username (default: "root")
- `password`: Database password (default: "test")
- `port`: Port to expose (default: 8529)
- `version`: ArangoDB version to use (default: "latest")
