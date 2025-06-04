# Wait Strategies

Testcontainers-Python provides several strategies to wait for containers to be ready before proceeding with tests. This is crucial for ensuring that your tests don't start before the container is fully initialized and ready to accept connections.

## Basic Wait Strategy

The simplest way to wait for a container is using the `wait_container_is_ready` decorator:

```python
from testcontainers.core.waiting_utils import wait_container_is_ready

class MyContainer(DockerContainer):
    @wait_container_is_ready()
    def _connect(self):
        # Your connection logic here
        pass
```

This decorator will retry the method until it succeeds or times out. By default, it will retry for 120 seconds with a 1-second interval between attempts.

## Log-based Waiting

Wait for specific log messages to appear:

```python
from testcontainers.core.waiting_utils import wait_for_logs

# Wait for a specific log message
container = GenericContainer(
    "nginx:alpine",
    wait=wait_for_logs("Configuration complete; ready for start")
)

# Wait for a log pattern using regex
container = GenericContainer(
    "postgres:latest",
    wait=wait_for_logs("database system is ready to accept connections")
)

# Wait for logs in both stdout and stderr
container = GenericContainer(
    "myapp:latest",
    wait=wait_for_logs("Ready", predicate_streams_and=True)
)
```

## HTTP-based Waiting

Wait for an HTTP endpoint to be accessible:

```python
from testcontainers.core.waiting_utils import wait_for_http

# Wait for an HTTP endpoint
container = GenericContainer(
    "nginx:alpine",
    wait=wait_for_http("/", port=80)
)

# Wait for a specific HTTP status code
container = GenericContainer(
    "myapp:latest",
    wait=wait_for_http("/health", port=8080, status_code=200)
)
```

## Custom Wait Conditions

You can create custom wait conditions by implementing your own wait function:

```python
def custom_wait(container):
    # Your custom logic here
    # Return True if the container is ready, False otherwise
    return True

container = GenericContainer(
    "myapp:latest",
    wait=custom_wait
)
```

## Connection-based Waiting

Many container implementations include built-in connection waiting. For example:

```python
from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer

# Redis container waits for connection
redis = RedisContainer()
redis.start()  # Will wait until Redis is ready to accept connections

# PostgreSQL container waits for connection
postgres = PostgresContainer()
postgres.start()  # Will wait until PostgreSQL is ready to accept connections
```

## Ryuk Container Wait Behavior

The Ryuk container (used for garbage collection) has its own wait mechanism that combines log-based and connection-based waiting:

1. **Log-based Wait**: Waits for the message ".\* Started!" with a 20-second timeout
2. **Connection Wait**: After the logs are found, attempts to establish a socket connection to the Ryuk container, retrying up to 50 times with a 0.5-second interval between attempts

This ensures that the Ryuk container is fully operational before any test containers are started.

## Configuring Wait Behavior

You can configure the wait behavior using environment variables:

- `TC_MAX_TRIES`: Maximum number of connection attempts (default: 120)
- `TC_POOLING_INTERVAL`: Time between connection attempts in seconds (default: 1)

Example:

```bash
export TC_MAX_TRIES=60
export TC_POOLING_INTERVAL=2
```

## Best Practices

1. Always use appropriate wait strategies for your containers
2. Set reasonable timeouts for your environment
3. Use specific wait conditions rather than generic ones when possible
4. Consider using connection-based waiting for database containers
5. Use log-based waiting for applications that output clear startup messages
6. Use HTTP-based waiting for web services
7. Implement custom wait conditions for complex startup scenarios
