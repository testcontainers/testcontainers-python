# How to Create a Container

Testcontainers-Python is a thin wrapper around Docker designed for use in tests. Anything you can run in Docker, you can spin up with Testcontainers-Python:

- NoSQL databases or other data stores (e.g. Redis, ElasticSearch, MongoDB)
- Web servers/proxies (e.g. NGINX, Apache)
- Log services (e.g. Logstash, Kibana)
- Other services developed by your team/organization which are already Dockerized

## Basic Container Creation

The simplest way to create a container is using the `GenericContainer` class:

```python
from testcontainers.generic import GenericContainer

def test_basic_container():
    with GenericContainer("nginx:alpine") as nginx:
        # Get container connection details
        host = nginx.get_container_host_ip()
        port = nginx.get_exposed_port(80)

        # Your test code here
        # For example, make HTTP requests to the nginx server
        import requests
        response = requests.get(f"http://{host}:{port}")
        assert response.status_code == 200
```

## Advanced Container Configuration

For more complex scenarios, use the `run` helper function. This high-level interface is similar to `docker run` and automatically handles:

- Creating temporary networks
- Mounting files or tmpfs
- Waiting for container readiness
- Container cleanup

Example with various configuration options:

```python
import io
import pytest
from testcontainers.core.container import run
from testcontainers.core.network import DockerNetwork
from testcontainers.core.waiting_utils import wait_for_logs

def test_nginx_advanced():
    # Create an isolated network
    network = DockerNetwork()
    network.create()
    pytest.addfinalizer(network.remove)

    # Create a test file to mount
    test_file_content = b"Hello from test file!"
    host_file = io.BytesIO(test_file_content)

    # Run the container with various options
    container = run(
        image="nginx:alpine",
        network=network.name,
        files=[(host_file, "/usr/share/nginx/html/test.txt")],  # Mount file
        tmpfs={"/tmp": "rw"},  # Mount tmpfs
        labels={"testcontainers.label": "true"},  # Add labels
        environment={"TEST": "true"},  # Set environment variables
        ports={"80/tcp": None},  # Expose port 80
        command=["nginx", "-g", "daemon off;"],  # Override default command
        wait=wait_for_logs("Configuration complete; ready for start"),  # Wait for logs
        startup_timeout=30,  # Set startup timeout
    )

    # Ensure cleanup
    pytest.addfinalizer(container.stop)
    pytest.addfinalizer(container.remove)

    # Test the container
    host = container.get_container_host_ip()
    port = container.get_exposed_port(80)

    # Verify the mounted file
    import requests
    response = requests.get(f"http://{host}:{port}/test.txt")
    assert response.text == "Hello from test file!"
```

## Container Lifecycle Management

Testcontainers-Python offers several ways to manage container lifecycle:

1. **Context manager (recommended):**
```python
with GenericContainer("nginx:alpine") as container:
    # Container is automatically started and stopped
    pass
```

2. **Manual management:**
```python
container = GenericContainer("nginx:alpine")
container.start()
try:
    # Your test code here
    pass
finally:
    container.stop()
    container.remove()
```

3. **Pytest fixtures:**
```python
import pytest
from testcontainers.generic import GenericContainer

@pytest.fixture
def nginx_container():
    container = GenericContainer("nginx:alpine")
    container.start()
    yield container
    container.stop()
    container.remove()

def test_with_nginx(nginx_container):
    # Your test code here
    pass
```

## Container Readiness

For details on waiting for containers to be ready, see [Wait strategies](wait_strategies.md).

## Best Practices

1. Always use context managers or ensure proper cleanup
2. Set appropriate timeouts for container startup
3. Use isolated networks for tests
4. Mount test files instead of copying them
5. Use tmpfs for temporary data
6. Add meaningful labels to containers
7. Configure proper wait conditions
