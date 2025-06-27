# CosmosDB

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.7.0"><span class="tc-version">:material-tag: v4.7.0</span></a>

## Introduction

The Testcontainers module for Azure Cosmos DB.

## Adding this module to your project dependencies

Please run the following command to add the CosmosDB module to your python dependencies:

```bash
pip install testcontainers[cosmosdb] pymongo azure-cosmos
```

## Usage example

<!--codeinclude-->

[Creating a CosmosDB container](../../modules/cosmosdb/example_basic.py)

<!--/codeinclude-->

## Features

- Multi-model database support (document, key-value, wide-column, graph)
- SQL-like query language
- Automatic indexing
- Partitioning support
- Global distribution
- Built-in aggregation functions
- Container management
- Document CRUD operations

## Configuration

The CosmosDB container can be configured with the following parameters:

- `port`: Port to expose (default: 8081)
- `version`: CosmosDB Emulator version to use (default: "latest")
- `ssl_verify`: Whether to verify SSL certificates (default: False)
- `emulator_key`: Emulator key for authentication (default: "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==")
