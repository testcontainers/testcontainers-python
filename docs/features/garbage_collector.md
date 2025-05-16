# Garbage Collector

Testcontainers for Python includes a robust garbage collection mechanism to ensure that containers are properly cleaned up, even in unexpected scenarios.

## How it Works

The garbage collection is implemented using a special container called "Ryuk" (pronounced "reaper"). This container is automatically started when you create your first test container and is responsible for cleaning up resources when:

1. The Python process exits normally
2. The Python process is terminated unexpectedly
3. The system crashes or loses power

## Configuration

The Ryuk container can be configured through environment variables:

- `TESTCONTAINERS_RYUK_DISABLED`: Set to `true` to disable the Ryuk container (not recommended)
- `TESTCONTAINERS_RYUK_CONTAINER_PRIVILEGED`: Set to `true` to run Ryuk in privileged mode (default: `false`)
- `TESTCONTAINERS_RYUK_RECONNECTION_TIMEOUT`: Timeout for Ryuk reconnection attempts (default: `10s`)

## Best Practices

1. **Don't Disable Ryuk**: The Ryuk container is an important part of Testcontainers' cleanup mechanism. Only disable it if you have a specific reason and understand the implications.

2. **Use Context Managers**: Always use the `with` statement when creating containers. This ensures proper cleanup even if an exception occurs:

```python
with RedisContainer() as redis:
    # Your test code here
```

3. **Session Management**: Each test session gets a unique session ID, and Ryuk tracks containers by this ID. This allows for proper cleanup even when running tests in parallel.

## Troubleshooting

If you notice containers not being cleaned up:

1. Check if Ryuk is running: `docker ps | grep testcontainers-ryuk`
2. Verify that the containers have the correct session label: `docker inspect <container_id> | grep session-id`
3. Check Ryuk logs: `docker logs <ryuk_container_id>`

## Implementation Details

The Ryuk container is a lightweight container that:

1. Connects to the Docker daemon
2. Listens for container events
3. Automatically removes containers when their parent process exits
4. Handles reconnection if the connection to Docker is lost

This provides a more reliable cleanup mechanism than relying solely on Python's garbage collection or process termination handlers.
