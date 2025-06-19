# Executing Commands in Containers

Testcontainers-Python provides several ways to execute commands inside containers. This is useful for setup, verification, and debugging during tests.

## Basic Command Execution

The simplest way to execute a command is using the `exec` method:

```python
from testcontainers.generic import GenericContainer

with GenericContainer("alpine:latest") as container:
    # Execute a simple command
    exit_code, output = container.exec(["ls", "-la"])
    print(output)  # Command output as string
```

## Command Execution with Options

You can customize command execution with various options:

```python
with GenericContainer("alpine:latest") as container:
    # Execute command with user
    exit_code, output = container.exec(
        ["whoami"],
        user="nobody"
    )

    # Execute command with environment variables
    exit_code, output = container.exec(
        ["echo", "$TEST_VAR"],
        environment={"TEST_VAR": "test_value"}
    )

    # Execute command with working directory
    exit_code, output = container.exec(
        ["pwd"],
        workdir="/tmp"
    )
```

## Interactive Commands

For interactive commands, you can use the `exec_interactive` method:

```python
with GenericContainer("alpine:latest") as container:
    # Start an interactive shell
    container.exec_interactive(["sh"])
```

## Command Execution with Timeout

You can set a timeout for command execution:

```python
with GenericContainer("alpine:latest") as container:
    # Execute command with timeout
    try:
        exit_code, output = container.exec(
            ["sleep", "10"],
            timeout=5  # Timeout in seconds
        )
    except TimeoutError:
        print("Command timed out")
```

## Command Execution with Privileges

For commands that require elevated privileges:

```python
with GenericContainer("alpine:latest") as container:
    # Execute command with privileges
    exit_code, output = container.exec(
        ["mount"],
        privileged=True
    )
```

## Command Execution with TTY

For commands that require a TTY:

```python
with GenericContainer("alpine:latest") as container:
    # Execute command with TTY
    exit_code, output = container.exec(
        ["top"],
        tty=True
    )
```

## Best Practices

1. Use appropriate timeouts for long-running commands
2. Handle command failures gracefully
3. Use environment variables for configuration
4. Consider security implications of privileged commands
5. Clean up after command execution
6. Use appropriate user permissions
7. Handle command output appropriately
8. Consider using shell scripts for complex commands

## Common Use Cases

### Database Setup

```python
from testcontainers.postgres import PostgresContainer

with PostgresContainer() as postgres:
    # Create a database
    postgres.exec(["createdb", "testdb"])

    # Run migrations
    postgres.exec(["psql", "-d", "testdb", "-f", "/path/to/migrations.sql"])
```

### File Operations

```python
with GenericContainer("alpine:latest") as container:
    # Create a directory
    container.exec(["mkdir", "-p", "/data"])

    # Set permissions
    container.exec(["chmod", "755", "/data"])

    # List files
    exit_code, output = container.exec(["ls", "-la", "/data"])
```

### Service Management

```python
with GenericContainer("nginx:alpine") as container:
    # Check service status
    exit_code, output = container.exec(["nginx", "-t"])

    # Reload configuration
    container.exec(["nginx", "-s", "reload"])
```

## Troubleshooting

If you encounter issues with command execution:

1. Check command syntax and arguments
2. Verify user permissions
3. Check container state
4. Verify command availability
5. Check for timeout issues
6. Verify environment variables
7. Check working directory
8. Verify TTY requirements
