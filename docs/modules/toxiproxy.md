# Toxiproxy

Since testcontainers-python <a href="https://github.com/testcontainers/testcontainers-python/releases/tag/v4.16.0"><span class="tc-version">:material-tag: v4.16.0</span></a>

## Introduction

The Testcontainers module for [Toxiproxy](https://github.com/Shopify/toxiproxy), a TCP proxy for
simulating adverse network conditions. Put Toxiproxy in front of a dependency and inject latency,
bandwidth limits, connection drops and other failures to test how your application behaves when its
dependencies misbehave.

## Adding this module to your project dependencies

Please run the following command to add the Toxiproxy module to your python dependencies:

```bash
pip install testcontainers[toxiproxy]
```

## Usage example

<!--codeinclude-->

[Injecting latency with Toxiproxy](toxiproxy_example.py)

<!--/codeinclude-->
