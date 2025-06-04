# ClickHouse

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.6.0"><span class="tc-version">:material-tag: v4.6.0</span></a>

## Introduction

The Testcontainers module for ClickHouse.

## Adding this module to your project dependencies

Please run the following command to add the ClickHouse module to your python dependencies:

```bash
pip install testcontainers[clickhouse] clickhouse-driver
```

## Usage example

<!--codeinclude-->

[Creating a ClickHouse container](../../modules/clickhouse/example_basic.py)

<!--/codeinclude-->

## Features

- Column-oriented storage
- High-performance analytics
- Real-time data processing
- SQL support
- Data compression
- Parallel processing
- Distributed queries
- Integration with pandas for data analysis

## Configuration

The ClickHouse container can be configured with the following parameters:

- `port`: Port to expose (default: 9000)
- `version`: ClickHouse version to use (default: "latest")
- `user`: Database username (default: "default")
- `password`: Database password (default: "")
- `database`: Database name (default: "default")
