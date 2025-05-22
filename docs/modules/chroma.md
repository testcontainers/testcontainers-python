# Chroma

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.6.0"><span class="tc-version">:material-tag: v4.6.0</span></a>

## Introduction

The Testcontainers module for Chroma.

## Adding this module to your project dependencies

Please run the following command to add the Chroma module to your python dependencies:

```bash
pip install testcontainers[chroma] chromadb requests
```

## Usage example

<!--codeinclude-->

[Creating a Chroma container](../../modules/chroma/example_basic.py)

<!--/codeinclude-->

## Features

- Vector similarity search
- Document storage and retrieval
- Metadata filtering
- Collection management
- Embedding storage
- Distance metrics
- Batch operations
- REST API support

## Configuration

The Chroma container can be configured with the following parameters:

- `port`: Port to expose (default: 8000)
- `version`: Chroma version to use (default: "latest")
- `persist_directory`: Directory to persist data (default: None)
- `allow_reset`: Whether to allow collection reset (default: True)
