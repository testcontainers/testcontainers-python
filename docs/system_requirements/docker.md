# Supported Docker environments

## Overview

Testcontainers requires a Docker-API compatible container runtime.
During development, Testcontainers is actively tested against recent versions of Docker on Linux, as well as against Docker Desktop on Mac and Windows.
These Docker environments are automatically detected and used by Testcontainers without any additional configuration being necessary.

It is possible to configure Testcontainers to work with alternative container runtimes (see further down for specific runtimes, or [Docker host detection](../features/configuration.md#docker-host-detection) for general configuration mechanisms).
Alternative container runtimes are not actively tested in the main development workflow, so not all Testcontainers features might be available and additional manual configuration might be necessary.

If you have further questions about configuration details for your setup or whether it supports running Testcontainers-based tests,
please contact the Testcontainers team and other users from the Testcontainers community on [Slack](https://slack.testcontainers.org/).

## Podman

In order to run testcontainers against [Podman](https://podman.io/), the env var below should be set.

Testcontainers auto-detects Podman from the daemon's `version` response and adapts a few behaviors (compose binary selection, port-binding parsing) accordingly.

**Linux (rootless):**

```bash
systemctl --user start podman.socket
export DOCKER_HOST="unix://${XDG_RUNTIME_DIR}/podman/podman.sock"
```

**Linux (rootful):**

```bash
sudo systemctl start podman.socket
export DOCKER_HOST="unix:///run/podman/podman.sock"
```

**macOS:**

```bash
export DOCKER_HOST="unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')"
```

You can also persist this in `~/.testcontainers.properties` as `docker.host=...`, or use a Docker context (`docker context use my-podman`).

### Docker Compose with Podman

`DockerCompose` prefers `docker` if it is on `PATH` (e.g. via the `podman-docker` shim). Otherwise, when Podman is detected, it falls back to the `podman` binary. You can always override the binary explicitly:

```python
DockerCompose(".", docker_command_path="podman")
```

Note that Podman does not support host port ranges (`published: "5000-5999"`) in compose files.
