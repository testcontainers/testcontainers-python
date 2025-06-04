# Docker Compose Support

Testcontainers-Python provides support for running Docker Compose environments in your tests. This is useful when you need to test against multiple containers that work together.

## Basic Usage

The simplest way to use Docker Compose is with the `DockerCompose` class:

```python
from testcontainers.compose import DockerCompose

# Create a compose environment
compose = DockerCompose(
    context="path/to/compose/directory",
    compose_file_name="docker-compose.yml"
)

# Start the environment
with compose:
    # Your test code here
    pass
```

## Configuration Options

The `DockerCompose` class supports various configuration options:

```python
compose = DockerCompose(
    context="path/to/compose/directory",
    compose_file_name=["docker-compose.yml", "docker-compose.override.yml"],  # Multiple compose files
    pull=True,  # Pull images before starting
    build=True,  # Build images before starting
    wait=True,  # Wait for services to be healthy
    env_file=".env",  # Environment file
    services=["service1", "service2"],  # Specific services to run
    profiles=["profile1", "profile2"],  # Compose profiles to use
    keep_volumes=False  # Whether to keep volumes after stopping
)
```

## Accessing Services

You can access service information and interact with containers:

```python
with DockerCompose("path/to/compose/directory") as compose:
    # Get service host and port
    host = compose.get_service_host("web")
    port = compose.get_service_port("web", 8080)

    # Get both host and port
    host, port = compose.get_service_host_and_port("web", 8080)

    # Execute commands in a container
    stdout, stderr, exit_code = compose.exec_in_container(
        ["ls", "-la"],
        service_name="web"
    )

    # Get container logs
    stdout, stderr = compose.get_logs("web")
```

## Waiting for Services

You can wait for services to be ready:

```python
with DockerCompose("path/to/compose/directory") as compose:
    # Wait for a specific URL to be accessible
    compose.wait_for("http://localhost:8080/health")
```

## Example with Multiple Services

Here's a complete example using multiple services:

```python
from testcontainers.compose import DockerCompose
import requests

def test_web_application():
    compose = DockerCompose(
        "path/to/compose/directory",
        compose_file_name="docker-compose.yml",
        pull=True,
        build=True
    )

    with compose:
        # Get web service details
        host = compose.get_service_host("web")
        port = compose.get_service_port("web", 8080)

        # Make a request to the web service
        response = requests.get(f"http://{host}:{port}/api/health")
        assert response.status_code == 200

        # Execute a command in the database service
        stdout, stderr, exit_code = compose.exec_in_container(
            ["psql", "-U", "postgres", "-c", "SELECT 1"],
            service_name="db"
        )
        assert exit_code == 0
```

## Best Practices

1. Use context managers (`with` statement) to ensure proper cleanup
2. Set appropriate timeouts for service startup
3. Use health checks in your compose files
4. Keep compose files in your test directory
5. Use environment variables for configuration
6. Consider using profiles for different test scenarios
7. Clean up volumes when not needed
8. Use specific service names in your tests
