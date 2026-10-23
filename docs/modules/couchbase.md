# Couchbase

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.16.0"><span class="tc-version">:material-tag: v4.16.0</span></a>

## Introduction

The Testcontainers module for [Couchbase Server](https://www.couchbase.com/products/server/).

## Adding this module to your project dependencies

Please run the following command to add the Couchbase module to your python dependencies:

```bash
pip install testcontainers[couchbase]
```

## Usage example

<!--codeinclude-->

[Creating a Couchbase container](couchbase_example.py)

<!--/codeinclude-->

## Features

- Single-node cluster with the Data, Query, Index and Search services
- Bucket, scope and collection created and ready before the container is returned
- Works with random host ports: the node advertises them through alternate addresses, so the SDK reaches every service
- Ready-to-use SDK `Cluster` through `client()`

## Configuration

The Couchbase container can be configured with the following parameters:

- `image`: Couchbase Server image to use (default: `couchbase/server:community-8.0.2`). Any Couchbase Server image works, including Enterprise Edition images such as `couchbase/server:enterprise-8.0.0`
- `username`: Cluster administrator username (default: `Administrator`, or the `COUCHBASE_USERNAME` environment variable)
- `password`: Cluster administrator password (default: `password`, or the `COUCHBASE_PASSWORD` environment variable)
- `bucket`: Bucket to create (default: `default`, or the `COUCHBASE_BUCKET` environment variable)
- `scope`: Scope to create in the bucket (default: `_default`, or the `COUCHBASE_SCOPE` environment variable)
- `collection`: Collection to create in the scope (default: `_default`, or the `COUCHBASE_COLLECTION` environment variable)
- `bucket_ram_quota_mb`: RAM quota of the bucket in MB (default: `256`)

The container needs about 1 GB of memory available to Docker.
