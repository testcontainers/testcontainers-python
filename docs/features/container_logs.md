# Container Logs

Testcontainers-Python provides several ways to access and follow container logs. This is essential for debugging and monitoring container behavior during tests.

## Basic Log Access

The simplest way to access logs is using the `get_logs` method:

```python
from testcontainers.generic import GenericContainer

with GenericContainer("nginx:alpine") as container:
    # Get all logs
    stdout, stderr = container.get_logs()
    print(f"STDOUT: {stdout}")
    print(f"STDERR: {stderr}")
```

## Following Logs

To follow logs in real-time:

```python
with GenericContainer("nginx:alpine") as container:
    # Follow logs
    for line in container.follow_logs():
        print(line)  # Each line as it appears
```

## Log Access with Options

You can customize log access with various options:

```python
with GenericContainer("nginx:alpine") as container:
    # Get logs with timestamps
    stdout, stderr = container.get_logs(timestamps=True)

    # Get logs since a specific time
    import datetime
    since = datetime.datetime.now() - datetime.timedelta(minutes=5)
    stdout, stderr = container.get_logs(since=since)

    # Get logs with tail
    stdout, stderr = container.get_logs(tail=100)  # Last 100 lines
```

## Log Streams

You can access specific log streams:

```python
with GenericContainer("nginx:alpine") as container:
    # Get only stdout
    stdout, _ = container.get_logs()

    # Get only stderr
    _, stderr = container.get_logs()

    # Get both streams
    stdout, stderr = container.get_logs()
```

## Log Following with Callback

You can use a callback function to process logs:

```python
def log_callback(line):
    print(f"Log line: {line}")

with GenericContainer("nginx:alpine") as container:
    # Follow logs with callback
    container.follow_logs(callback=log_callback)
```

## Log Access in Tests

Here's how to use logs in tests:

```python
import pytest
from testcontainers.generic import GenericContainer

def test_container_logs():
    with GenericContainer("nginx:alpine") as container:
        # Wait for specific log message
        for line in container.follow_logs():
            if "Configuration complete" in line:
                break

        # Verify log content
        stdout, stderr = container.get_logs()
        assert "Configuration complete" in stdout
```

## Best Practices

1. Use appropriate log levels
2. Handle log streams separately
3. Use timestamps for debugging
4. Consider log rotation
5. Use log following for real-time monitoring
6. Clean up log resources
7. Use appropriate log formats
8. Consider log volume

## Common Use Cases

### Application Startup Verification

```python
with GenericContainer("myapp:latest") as container:
    # Wait for application to start
    for line in container.follow_logs():
        if "Application started" in line:
            break
```

### Error Detection

```python
with GenericContainer("myapp:latest") as container:
    # Monitor for errors
    for line in container.follow_logs():
        if "ERROR" in line:
            print(f"Error detected: {line}")
```

### Performance Monitoring

```python
with GenericContainer("myapp:latest") as container:
    # Monitor performance metrics
    for line in container.follow_logs():
        if "Performance" in line:
            print(f"Performance metric: {line}")
```

## Troubleshooting

If you encounter issues with log access:

1. Check container state
2. Verify log configuration
3. Check for log rotation
4. Verify log permissions
5. Check for log volume
6. Verify log format
7. Check for log buffering
8. Verify log drivers
