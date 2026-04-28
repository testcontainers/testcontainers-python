# MongoDB

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.6.0"><span class="tc-version">:material-tag: v4.6.0</span></a>

## Introduction

The Testcontainers module for MongoDB.

This module provides two container classes:

- **`MongoDbContainer`** — wraps the standard [`mongo`](https://hub.docker.com/_/mongo) image for general-purpose MongoDB testing.
- **`MongoDBAtlasLocalContainer`** — wraps the [`mongodb/mongodb-atlas-local`](https://hub.docker.com/r/mongodb/mongodb-atlas-local) image, providing a local MongoDB Atlas deployment with support for Atlas-specific features such as **Atlas Search** and **Atlas Vector Search**.

## Adding this module to your project dependencies

Please run the following command to add the MongoDB module to your python dependencies:

```bash
pip install testcontainers[mongodb] pymongo
```

## Usage example

<!--codeinclude-->

[Creating a MongoDB container](../../modules/mongodb/example_basic.py)

<!--/codeinclude-->
