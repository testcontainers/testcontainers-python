# Advanced Features and Best Practices

This document covers advanced features and best practices for using testcontainers-python in complex scenarios.

## Docker-in-Docker (DinD) Support

Testcontainers-python provides robust support for running tests inside Docker containers, enabling true isolation and reproducibility of test environments. This feature is particularly valuable for CI/CD pipelines, integration testing, and scenarios requiring consistent, isolated environments.

### Use Cases

- **CI/CD Pipelines**: Run tests in isolated containers within your CI environment
- **Integration Testing**: Test interactions between multiple services in a controlled environment
- **Environment Consistency**: Ensure tests run in the same environment across different machines
- **Resource Isolation**: Prevent test interference and resource conflicts

### Connection Modes

Testcontainers-python supports three connection modes for container networking:

- **`bridge_ip`**: Use this mode when containers need to communicate over a bridge network. This is the default mode and provides isolated network communication between containers.
- **`gateway_ip`**: Use this mode when containers need to access the host network. This is useful when containers need to communicate with services running on the host machine.
- **`docker_host`**: Use this mode for local development. This mode uses the host's Docker socket directly, which is more efficient but provides less isolation.

### Network Configuration

Here's how to set up container networking:

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

# Create an isolated network
network = Network()

# Create containers on the network
container1 = DockerContainer("nginx:alpine")
container1.with_network(network)
container1.with_network_aliases(["web"])

container2 = DockerContainer("redis:alpine")
container2.with_network(network)
container2.with_network_aliases(["cache"])
```

### Volume Mounting

Mount host directories into containers for data persistence or configuration:

```python
container = DockerContainer("nginx:alpine")
container.with_volume_mapping("/host/path", "/container/path", "ro")  # Read-only mount
container.with_volume_mapping("/host/data", "/container/data", "rw")  # Read-write mount
```

### Best Practices

When working with Docker-in-Docker, it's crucial to follow a comprehensive set of best practices to ensure optimal performance, security, and maintainability. Start by carefully managing your resources: set appropriate memory and CPU limits for your containers, actively monitor their resource usage, and ensure proper cleanup after tests complete. This helps prevent resource exhaustion and maintains system stability.

Security should be a top priority in your DinD implementation. Always use read-only volume mounts when possible to prevent unauthorized modifications, avoid running containers with privileged access unless absolutely necessary, and implement proper network isolation to prevent unauthorized access between containers. These measures help maintain a secure testing environment.

For optimal performance, focus on using appropriate base images. Alpine-based images are often a good choice due to their small footprint, but consider your specific needs. Implement proper health checks to ensure containers are truly ready before proceeding with tests, and consider using container caching strategies to speed up test execution. When dealing with complex setups, consider using Docker Compose to manage multiple containers and their interactions.

## ARM64 Support

Testcontainers-python provides comprehensive support for ARM64 architecture through automatic emulation, making it seamless to run tests on ARM-based systems like Apple Silicon (M1/M2) Macs and ARM-based cloud instances.

### Using ARM64 Support

```python
from testcontainers.core.container import DockerContainer

# Basic usage with automatic emulation
container = DockerContainer("nginx:alpine")
container.maybe_emulate_amd64()  # Automatically handles ARM64 emulation

# Advanced configuration with resource limits
container = DockerContainer("nginx:alpine")
container.maybe_emulate_amd64()
container.with_memory_limit("512m")
container.with_cpu_limit(0.5)  # Use 50% of available CPU
```

### Performance Considerations

1. **Emulation Overhead**:
     - Expect 20-30% performance impact when running x86_64 containers on ARM
     - Use ARM-native images when available for better performance
     - Consider using multi-architecture images (e.g., `nginx:alpine`)

2. **Resource Management**:
     - Monitor memory usage during emulation
     - Adjust CPU limits based on your workload
     - Use appropriate base images to minimize emulation overhead

### Best Practices

When working with ARM64 architecture, a thoughtful approach to image selection and resource management is essential. Prioritize using multi-architecture images when available, as they provide the best compatibility across different platforms. For optimal performance, use minimal base images to reduce emulation overhead, and thoroughly test your setup with different image variants to find the best balance between size and functionality.

In your development workflow, ensure you test your applications on both ARM and x86_64 environments to catch any architecture-specific issues early. When setting up CI/CD pipelines, make sure they support ARM64 architecture and document any architecture-specific considerations in your project documentation. This helps maintain consistency across different development environments and deployment targets.

## TCP Forwarding with Socat

The `SocatContainer` provides powerful TCP forwarding capabilities, enabling complex networking scenarios and service communication patterns.

### Using Socat Container

```python
from testcontainers.socat import SocatContainer

# Basic TCP forwarding
socat = SocatContainer()
socat.with_target(8080, "host.docker.internal", 80)
socat.start()

# Multiple port forwarding
socat = SocatContainer()
socat.with_target(8080, "host.docker.internal", 80)
socat.with_target(5432, "postgres", 5432)  # Forward to another container
socat.start()

# UDP forwarding
socat = SocatContainer()
socat.with_target(53, "8.8.8.8", 53, protocol="udp")
socat.start()
```

### Advanced Configuration

```python
# Custom Socat options
socat = SocatContainer()
socat.with_option("-d")  # Enable debug output
socat.with_option("-v")  # Verbose mode
socat.with_target(8080, "host.docker.internal", 80)
socat.start()
```

### Best Practices

When working with Socat, security should be your primary concern. Only forward the ports that are absolutely necessary for your application to function, and implement appropriate access controls to prevent unauthorized access. For sensitive traffic, consider using TLS to encrypt the forwarded connections. Regularly monitor your forwarded connections to detect any suspicious activity or performance issues.

Performance optimization is crucial for maintaining a responsive system. Monitor connection latency to identify potential bottlenecks, and adjust buffer sizes based on your specific use case. For high-load scenarios, consider implementing connection pooling to manage resources efficiently. Regular maintenance is also important: document your forwarding rules clearly, implement proper cleanup procedures, and monitor connection health to ensure reliable operation.

## Environment Variables and Configuration

Testcontainers-python offers flexible configuration options through environment variables, configuration files, and properties.

### Using Environment Variables

**Direct Environment Variables**:

```python
container = DockerContainer("nginx:alpine")
container.with_env("NGINX_HOST", "example.com")
container.with_env("NGINX_PORT", "8080")
container.with_env("DEBUG", "true")
```

**Environment Files**:

```python
# .env file
NGINX_HOST=example.com
NGINX_PORT=8080
DEBUG=true

# Python code
container = DockerContainer("nginx:alpine")
container.with_env_file(".env")
```

**Configuration Properties**:

```properties
# .testcontainers.properties
ryuk.container.privileged=true
ryuk.reconnection.timeout=10s
docker.client.strategy=org.testcontainers.dockerclient.UnixSocketClientProviderStrategy
```

### Best Practices

Configuration management in testcontainers-python requires a careful balance between flexibility and security. Never commit sensitive data to version control; instead, use environment variables for secrets and consider implementing a secrets manager for more complex scenarios. When dealing with configuration files, ensure they are well-documented and include validation to catch errors early.

In your development workflow, provide example configuration files to help new team members get started quickly. Document all required environment variables and their purposes, and implement configuration testing to catch issues before they reach production. Use configuration templates to maintain consistency across different environments while allowing for environment-specific customization.

## Container Health Checks

Testcontainers-python provides robust health checking mechanisms to ensure containers are ready for testing.

### Custom Health Checks

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
import requests

class WebContainer(DockerContainer):
    @wait_container_is_ready()
    def _connect(self):
        response = requests.get(f"http://{self.get_container_host_ip()}:{self.get_exposed_port(80)}")
        return response.status_code == 200

class DatabaseContainer(DockerContainer):
    @wait_container_is_ready()
    def _connect(self):
        # Implement database connection check
        pass
```

### Health Check Strategies

1. **HTTP Health Checks**:
     - Check HTTP endpoints
     - Verify response status codes
     - Validate response content

2. **TCP Health Checks**:
     - Verify port availability
     - Check connection establishment
     - Monitor connection stability

3. **Application-Specific Checks**:
     - Verify service readiness
     - Check data consistency
     - Validate business logic

### Best Practices

Health checks are a critical component of reliable containerized applications. When implementing health checks, use appropriate timeouts and implement retry mechanisms to handle temporary issues gracefully. Log health check failures with sufficient detail to aid in debugging, and consider using multiple check strategies to ensure comprehensive coverage of your application's health.

Monitoring is essential for maintaining system health. Track health check metrics to identify patterns and potential issues, implement proper logging to capture relevant information, and set up alerts for failures to enable quick response to problems. Regular maintenance is also important: review your health checks periodically, update check criteria as your application evolves, and test check reliability to ensure they continue to provide accurate information.

## Error Handling and Debugging

### Common Issues and Solutions

**Container Startup Failures**:

```python
try:
    container = DockerContainer("nginx:alpine")
    container.start()
except Exception as e:
    print(f"Container startup failed: {e}")
    print(f"Container logs: {container.get_logs()}")
    raise
```

**Network Issues**:

```python
# Debug network configuration
container_id = container.get_wrapped_container().id
network_info = container.get_docker_client().inspect_network(network_name)
print(f"Network configuration: {network_info}")

# Check container connectivity
host_ip = container.get_container_host_ip()
print(f"Container host IP: {host_ip}")
```

**Resource Cleanup**:

```python
from contextlib import contextmanager

@contextmanager
def managed_container():
    container = DockerContainer("nginx:alpine")
    try:
        container.start()
        yield container
    finally:
        container.stop()
        container.remove()
```

### Debugging Tools

**Container Logs**:

```python
# Get all logs
stdout, stderr = container.get_logs()

# Get recent logs
stdout, stderr = container.get_logs(since="2024-01-01T00:00:00Z")

# Follow logs
for line in container.get_logs(stream=True):
    print(line)
```

**Container Information**:

```python
# Get container details
container_id = container.get_wrapped_container().id
container_info = container.get_docker_client().inspect_container(container_id)

# Get resource usage
stats = container.get_docker_client().stats(container_id)
```

**Network Information**:

```python
# Get network details
network_name = container.get_docker_client().network_name(container_id)
network_info = container.get_docker_client().inspect_network(network_name)

# List connected containers
connected_containers = container.get_docker_client().list_containers(
    filters={"network": network_name}
)
```

### Best Practices

Error handling and debugging in containerized environments require a systematic approach. Start by implementing proper validation and using appropriate timeouts to prevent common issues. Set up monitoring to catch problems early, and document known issues and their solutions to help team members resolve similar problems quickly.

When debugging issues, collect relevant logs and analyze error patterns to identify root causes. Use appropriate tools for different types of problems, and document your solutions to build a knowledge base for future reference. Regular maintenance is crucial: perform regular system checks, keep documentation up to date, monitor error rates, and implement improvements based on your findings.

## Performance Optimization

Optimizing the performance of your testcontainers-python setup is crucial for maintaining efficient test execution and resource utilization. This section covers key strategies and best practices for achieving optimal performance.

### Image Selection and Management

The choice of base images significantly impacts your container's performance and resource usage. When selecting images, consider the following:

```python
# Using minimal base images
container = DockerContainer("nginx:alpine")  # ~7MB
container = DockerContainer("python:3.9-slim")  # ~125MB
container = DockerContainer("python:3.9")  # ~900MB

# Using multi-stage builds for custom images
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient

client = DockerClient()
client.build_image(
    path=".",
    tag="my-optimized-app:latest",
    dockerfile="""
    FROM python:3.9-slim as builder
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    FROM python:3.9-slim
    WORKDIR /app
    COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
    COPY . .
    """
)
```

### Resource Management

Proper resource allocation is essential for maintaining system stability and performance. Here's how to manage resources effectively:

```python
# Setting resource limits
container = DockerContainer("nginx:alpine")
container.with_memory_limit("512m")  # Limit memory usage
container.with_cpu_limit(0.5)  # Use 50% of available CPU
container.with_shm_size("256m")  # Set shared memory size

# Monitoring resource usage
stats = container.get_docker_client().stats(container.get_wrapped_container().id)
print(f"CPU Usage: {stats['cpu_stats']['cpu_usage']['total_usage']}")
print(f"Memory Usage: {stats['memory_stats']['usage']}")
```

### Parallel Execution

Running tests in parallel can significantly reduce overall execution time. Here's how to implement parallel execution:

```python
import concurrent.futures
from testcontainers.core.container import DockerContainer

def run_test(container_config):
    with DockerContainer(**container_config) as container:
        # Run your test
        pass

# Run multiple containers in parallel
container_configs = [
    {"image": "nginx:alpine", "ports": {"80": 8080}},
    {"image": "redis:alpine", "ports": {"6379": 6379}},
    {"image": "postgres:alpine", "ports": {"5432": 5432}}
]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(run_test, config) for config in container_configs]
    concurrent.futures.wait(futures)
```

### Caching Strategies

Implementing effective caching strategies can significantly improve test execution time:

```python
# Using Docker layer caching
container = DockerContainer("python:3.9-slim")
container.with_volume_mapping(
    "${HOME}/.cache/pip",  # Host pip cache
    "/root/.cache/pip",    # Container pip cache
    "rw"
)

# Using build cache
client = DockerClient()
client.build_image(
    path=".",
    tag="my-app:latest",
    dockerfile="Dockerfile",
    buildargs={"BUILDKIT_INLINE_CACHE": "1"}
)
```
