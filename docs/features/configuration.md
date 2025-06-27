# Custom Configuration

You can override some default properties if your environment requires it.

## Configuration Locations

The configuration will be loaded from multiple locations. Properties are considered in the following order:

1. Environment variables
2. `.testcontainers.properties` in the user's home folder. Example locations:
   **Linux:** `/home/myuser/.testcontainers.properties`
   **Windows:** `C:/Users/myuser/.testcontainers.properties`
   **macOS:** `/Users/myuser/.testcontainers.properties`

Note that when using environment variables, configuration property names should be set in uppercase with underscore separators, preceded by `TESTCONTAINERS_` - e.g. `ryuk.disabled` becomes `TESTCONTAINERS_RYUK_DISABLED`.

### Supported Properties

Testcontainers-Python provides a configuration class to represent the settings:

```python
from testcontainers.core.config import TestcontainersConfiguration

# Default configuration
config = TestcontainersConfiguration()

# Access configuration values
max_tries = config.max_tries
sleep_time = config.sleep_time
ryuk_image = config.ryuk_image
ryuk_privileged = config.ryuk_privileged
ryuk_disabled = config.ryuk_disabled
ryuk_docker_socket = config.ryuk_docker_socket
ryuk_reconnection_timeout = config.ryuk_reconnection_timeout
tc_host_override = config.tc_host_override
```

The following properties are supported:

| Property                    | Environment Variable                        | Description                                          | Default                   |
| --------------------------- | ------------------------------------------- | ---------------------------------------------------- | ------------------------- |
| `tc.host`                   | `TC_HOST` or `TESTCONTAINERS_HOST_OVERRIDE` | Testcontainers host address                          | -                         |
| `docker.host`               | `DOCKER_HOST`                               | Address of the Docker daemon                         | -                         |
| `docker.tls.verify`         | `DOCKER_TLS_VERIFY`                         | Enable/disable TLS verification                      | 0                         |
| `docker.cert.path`          | `DOCKER_CERT_PATH`                          | Path to Docker certificates                          | -                         |
| `ryuk.disabled`             | `TESTCONTAINERS_RYUK_DISABLED`              | Disable the Garbage Collector                        | false                     |
| `ryuk.container.privileged` | `TESTCONTAINERS_RYUK_PRIVILEGED`            | Run Ryuk in privileged mode                          | false                     |
| `ryuk.reconnection.timeout` | `RYUK_RECONNECTION_TIMEOUT`                 | Time to wait before reconnecting                     | 10s                       |
| `ryuk.image`                | `RYUK_CONTAINER_IMAGE`                      | Ryuk container image                                 | testcontainers/ryuk:0.8.1 |
| `connection.mode`           | `TESTCONTAINERS_CONNECTION_MODE`            | Connection mode (bridge_ip, gateway_ip, docker_host) | -                         |

Additional configuration options:

| Environment Variable  | Description                                 | Default |
| --------------------- | ------------------------------------------- | ------- |
| `TC_MAX_TRIES`        | Maximum number of connection attempts       | 120     |
| `TC_POOLING_INTERVAL` | Time between connection attempts            | 1       |
| `DOCKER_AUTH_CONFIG`  | Docker authentication config (experimental) | -       |

## Docker Host Detection

Testcontainers-Python will attempt to detect the Docker environment and configure everything to work automatically.

However, sometimes customization is required. Testcontainers-Python will respect the following order:

1. Read the **tc.host** property in the `~/.testcontainers.properties` file. E.g. `tc.host=tcp://my.docker.host:1234`

2. Read the **TC_HOST** or **TESTCONTAINERS_HOST_OVERRIDE** environment variable. E.g. `TC_HOST=tcp://my.docker.host:1234`

3. Read the **DOCKER_HOST** environment variable. E.g. `DOCKER_HOST=unix:///var/run/docker.sock`
   See [Docker environment variables](https://docs.docker.com/engine/reference/commandline/cli/#environment-variables) for more information.

4. Read the default Docker socket path, without the unix schema. E.g. `/var/run/docker.sock`

5. Read the **docker.host** property in the `~/.testcontainers.properties` file. E.g. `docker.host=tcp://my.docker.host:1234`

6. Read the rootless Docker socket path, checking the following alternative locations:

   1. `${XDG_RUNTIME_DIR}/.docker/run/docker.sock`
   2. `${HOME}/.docker/run/docker.sock`
   3. `${HOME}/.docker/desktop/docker.sock`
   4. `/run/user/${UID}/docker.sock`, where `${UID}` is the user ID of the current user

7. The library will raise a `DockerHostError` if none of the above are set, meaning that the Docker host was not detected.

## Docker Socket Path Detection

Testcontainers-Python will attempt to detect the Docker socket path and configure everything to work automatically.

However, sometimes customization is required. Testcontainers-Python will respect the following order:

1. Read the **TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE** environment variable. Path to Docker's socket. Used by Ryuk, Docker Compose, and a few other containers that need to perform Docker actions.
   Example: `/var/run/docker-alt.sock`

2. If the operating system retrieved by the Docker client is "Docker Desktop", and the host is running on Windows, it will return the `//var/run/docker.sock` UNC path. Otherwise, it returns the default Docker socket path for rootless Docker.

3. Get the current Docker host from the existing strategies: see Docker host detection.

4. If the socket contains the unix schema, the schema is removed (e.g. `unix:///var/run/docker.sock` -> `/var/run/docker.sock`)

5. Otherwise, the default location of the Docker socket is used: `/var/run/docker.sock`

The library will raise a `DockerHostError` if the Docker host cannot be discovered.

## Connection Modes

Testcontainers-Python supports different connection modes that determine how containers are accessed:

1. `bridge_ip` (default): Uses the bridge network IP address
2. `gateway_ip`: Uses the gateway IP address
3. `docker_host`: Uses the Docker host address

You can set the connection mode using the `TESTCONTAINERS_CONNECTION_MODE` environment variable or the `connection.mode` property in `.testcontainers.properties`.

## Example Configuration File

Here's an example of a `.testcontainers.properties` file:

```properties
# Docker host configuration
docker.host=tcp://my.docker.host:1234
docker.tls.verify=1
docker.cert.path=/path/to/certs

# Ryuk configuration
ryuk.disabled=false
ryuk.container.privileged=true
ryuk.reconnection.timeout=30s
ryuk.image=testcontainers/ryuk:0.8.1

# Testcontainers configuration
tc.host=tcp://my.testcontainers.host:1234
connection.mode=bridge_ip
```

## Using Configuration in Code

You can access and modify the configuration programmatically:

```python
from testcontainers.core.config import testcontainers_config

# Access configuration values
max_tries = testcontainers_config.max_tries
sleep_time = testcontainers_config.sleep_time

# The configuration is read-only by default
# Changes should be made through environment variables or .testcontainers.properties
```

## Best Practices

1. Use environment variables for CI/CD environments
2. Use `.testcontainers.properties` for local development
3. Set appropriate timeouts for your environment
4. Enable verbose logging when debugging
5. Consider disabling Ryuk if your environment already handles container cleanup
6. Use privileged mode for Ryuk only when necessary
7. Set proper TLS verification and certificate paths for secure environments
8. Choose the appropriate connection mode for your environment
