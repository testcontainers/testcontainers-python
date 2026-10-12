# Meilisearch

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.15.0"><span class="tc-version">:material-tag: v4.15.0</span></a>

## Introduction

The Testcontainers module for Meilisearch.

## Adding this module to your project dependencies

Please run the following command to add the Meilisearch module to your python dependencies:

```bash
pip install testcontainers[meilisearch] meilisearch
```

## Usage example

<!--codeinclude-->

[Creating a Meilisearch container](meilisearch_example.py)

<!--/codeinclude-->

## Configuration

The Meilisearch container can be configured with the following parameters:

- `image`: Docker image to use (default: `getmeili/meilisearch:v1.53`)
- `port`: Port to expose (default: `7700`)
- `meili_env`: Value of `MEILI_ENV` (default: `production`)
- `master_key`: Master key; a random one is generated if not provided. Must be at least 16 bytes when `meili_env` is `production`