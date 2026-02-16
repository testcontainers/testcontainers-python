# Temporal

## Introduction

The Testcontainers module for [Temporal](https://temporal.io/) — a durable execution platform for running reliable, long-running workflows.

This module spins up the Temporal dev server (`temporalio/auto-setup`) which includes the Temporal server, a preconfigured `default` namespace, and the Web UI.

## Adding this module to your project dependencies

Please run the following command to add the Temporal module to your python dependencies:

```bash
pip install testcontainers[temporal]
```

To interact with the server you will also need a Temporal SDK, for example:

```bash
pip install temporalio
```

## Usage example

<!--codeinclude-->

[Creating a Temporal container](../../modules/temporal/example_basic.py)

<!--/codeinclude-->
