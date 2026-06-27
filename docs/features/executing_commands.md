# Executing Commands in Containers

Testcontainers-Python provides several ways to execute commands inside containers. This is useful for setup, verification, and debugging during tests.

## Basic Command Execution

The simplest way to execute a command is using the `exec` method, passing either an argv list or a string:

```python
from testcontainers.core.container import DockerContainer

with DockerContainer("alpine:latest") as container:
    # Execute a simple command (argv form)
    result = container.exec(["ls", "-la"])
    print(result.exit_code)       # 0
    print(result.output)          # command output as bytes
    print(result.output.decode()) # ...decoded to str

    # A string is also accepted
    result = container.exec("ls -la")
```

`exec` returns a named `(exit_code, output)` tuple, so you can also unpack it directly:

```python
exit_code, output = container.exec(["ls", "-la"])
```

> **A string command is *not* run through a shell.** `docker-py` tokenizes it with `shlex.split`, so shell features such as pipes, redirections, and variable expansion are passed through literally — `container.exec("echo $HOME")` prints the text `$HOME`, not your home directory. When you need shell behavior, invoke a shell explicitly: `container.exec(["sh", "-c", "echo $HOME"])`.

## Command Execution with Options

To customize how a command runs — the user, environment, or working directory — pass an `ExecConfig`:

```python
from testcontainers.core.container import DockerContainer, ExecConfig

with DockerContainer("alpine:latest") as container:
    # Execute command as a specific user
    result = container.exec(ExecConfig(command=["whoami"], user="nobody"))

    # Execute command with environment variables
    # (use a command that reads the environment, e.g. printenv -- a bare
    # argv command is not shell-expanded, see the note above)
    result = container.exec(ExecConfig(command=["printenv", "TEST_VAR"], environment={"TEST_VAR": "test_value"}))

    # Execute command in a working directory (str or pathlib.Path)
    result = container.exec(ExecConfig(command=["pwd"], workdir="/tmp"))
```

`ExecConfig` is a frozen dataclass: only `command` is required, and `user`, `environment`, `workdir`, and `privileged` are optional. Because it is immutable, the idiomatic way to derive a variant is `dataclasses.replace`:

```python
from dataclasses import replace

base = ExecConfig(command=["pwd"], workdir="/tmp")
in_var = replace(base, workdir="/var")
```

## Command Execution with Privileges

For commands that require elevated privileges, set `privileged=True`:

```python
from testcontainers.core.container import DockerContainer, ExecConfig

with DockerContainer("alpine:latest") as container:
    # Execute command with privileges
    result = container.exec(ExecConfig(command=["mount"], privileged=True))
```

## Best Practices

1. Handle command failures gracefully — check `exit_code` rather than assuming success
2. Use environment variables for configuration
3. Consider security implications of privileged commands
4. Clean up after command execution
5. Use appropriate user permissions
6. Decode `output` from bytes when you need text
7. Use an explicit `["sh", "-c", ...]` invocation for commands that rely on shell features

## Common Use Cases

### Database Setup

```python
from testcontainers.community.postgres import PostgresContainer

with PostgresContainer() as postgres:
    # Create a database
    postgres.exec(["createdb", "testdb"])

    # Run migrations
    postgres.exec(["psql", "-d", "testdb", "-f", "/path/to/migrations.sql"])
```

### File Operations

```python
from testcontainers.core.container import DockerContainer

with DockerContainer("alpine:latest") as container:
    # Create a directory
    container.exec(["mkdir", "-p", "/data"])

    # Set permissions
    container.exec(["chmod", "755", "/data"])

    # List files
    result = container.exec(["ls", "-la", "/data"])
```

### Service Management

```python
from testcontainers.core.container import DockerContainer

with DockerContainer("nginx:alpine") as container:
    # Check service status
    result = container.exec(["nginx", "-t"])

    # Reload configuration
    container.exec(["nginx", "-s", "reload"])
```

## Troubleshooting

If you encounter issues with command execution:

1. Check command syntax and arguments
2. Verify user permissions
3. Check container state
4. Verify command availability
5. Verify environment variables
6. Check the working directory
7. Remember that string commands are tokenized, not shell-interpreted
