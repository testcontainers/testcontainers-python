# Networking and Container Communication

Testcontainers-Python provides several ways to configure networking between containers and your test code. This is essential for testing distributed systems and microservices.

## Connection Modes

Testcontainers-Python supports three connection modes that determine how containers are accessed:

1. `bridge_ip` (default): Uses the bridge network IP address. Best for:

     - Docker-in-Docker (DinD) scenarios
     - When containers need to communicate over a bridge network
     - When you need direct container-to-container communication

2. `gateway_ip`: Uses the gateway IP address. Best for:

     - Docker-in-Docker (DinD) scenarios
     - When containers need to access the host network
     - When you need to access services running on the host

3. `docker_host`: Uses the Docker host address. Best for:

     - Local development
     - When running tests outside of containers
     - When you need to access containers from the host machine

You can set the connection mode using the `TESTCONTAINERS_CONNECTION_MODE` environment variable or the `connection.mode` property in `.testcontainers.properties`.

## Port Exposure

Testcontainers-Python provides two methods for exposing container ports, with `with_exposed_ports` being the recommended approach:

### Exposing Ports with Random Host Ports (Recommended)

```python
from testcontainers.core.container import DockerContainer

container = DockerContainer("nginx:alpine")
container.with_exposed_ports(80, "443/tcp")  # Expose ports, host ports will be assigned randomly
container.start()
mapped_port = container.get_exposed_port(80)  # Get the randomly assigned host port
```

This is the preferred method because it:

- Avoids port conflicts in parallel test execution
- Is more secure as it doesn't expose fixed ports
- Matches the behavior of other testcontainers implementations
- Allows for better isolation between test runs

### Binding to Specific Host Ports (Not Recommended)

```python
container = DockerContainer("nginx:alpine")
container.with_bind_ports(80, 8080)  # Map container port 80 to host port 8080
container.with_bind_ports("443/tcp", 8443)  # Map container port 443 to host port 8443
```

Use `with_bind_ports` only in specific cases where you absolutely need a fixed port number, such as:

- When testing with tools that require specific port numbers
- When integrating with external systems that can't handle dynamic ports
- When debugging and need consistent port numbers

Note that using fixed ports can cause conflicts when running tests in parallel and may lead to test failures if the specified ports are already in use.

## Creating Networks

You can create isolated networks for your containers:

```python
from testcontainers.core.network import Network

# Create a new network
network = Network()
network.create()

# Use the network with containers
container1 = GenericContainer("nginx:alpine")
container1.with_network(network)
container1.with_network_aliases(["web"])

container2 = GenericContainer("redis:alpine")
container2.with_network(network)
container2.with_network_aliases(["cache"])

# Start containers
with container1, container2:
    # Containers can communicate using their network aliases
    # e.g., "web" can connect to "cache:6379"
    pass
```

## Container Communication

Containers can communicate with each other in several ways:

1. Using network aliases:

```python
# Container 1 can reach Container 2 using its network alias
container1 = GenericContainer("app:latest")
container1.with_network(network)
container1.with_network_aliases(["app"])

container2 = GenericContainer("db:latest")
container2.with_network(network)
container2.with_network_aliases(["database"])

# Container 1 can connect to Container 2 using "database:5432"
```

2. Using container IP addresses:

```python
with container1, container2:
    # Get container IP addresses
    container1_ip = container1.get_container_host_ip()
    container2_ip = container2.get_container_host_ip()

    # Containers can communicate using IP addresses
    # e.g., container1 can connect to container2_ip:5432
```

3. Using host networking:

```python
container = GenericContainer("nginx:alpine")
container.with_network_mode("host")  # Use host networking
```

## Example: Multi-Container Application

Here's a complete example of a multi-container application:

```python
from testcontainers.core.network import Network
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

def test_multi_container_app():
    # Create a network
    network = Network()
    network.create()

    # Create containers
    postgres = PostgresContainer()
    postgres.with_network(network)
    postgres.with_network_aliases(["db"])

    redis = RedisContainer()
    redis.with_network(network)
    redis.with_network_aliases(["cache"])

    # Start containers
    with postgres, redis:
        # Get connection details
        db_host = postgres.get_container_host_ip()
        db_port = postgres.get_exposed_port(5432)

        redis_host = redis.get_container_host_ip()
        redis_port = redis.get_exposed_port(6379)

        # Your test code here
        pass
```

## Best Practices

1. **Port Management**:

     - Always use `with_exposed_ports` instead of `with_bind_ports` unless you have a specific requirement for fixed ports
     - Use `get_exposed_port` to retrieve the mapped port number when using `with_exposed_ports`
     - Avoid hardcoding port numbers in your tests

2. **Network Configuration**:

     - Use isolated networks for tests to prevent conflicts
     - Use meaningful network aliases for better readability and maintainability
     - Avoid using host networking unless absolutely necessary
     - Use the appropriate connection mode for your environment:
        - `bridge_ip` for Docker-in-Docker (DinD) scenarios
        - `gateway_ip` for accessing host network services
        - `docker_host` for local development

3. **Container Communication**:

     - Use network aliases for container-to-container communication
     - Use environment variables for configuration
     - Consider using Docker Compose for complex multi-container setups

4. **Resource Management**:

     - Always use context managers (`with` statements) to ensure proper cleanup
     - Let the Ryuk container handle cleanup in case of unexpected termination
     - Clean up networks after tests
     - Use environment variables for configuration

5. **Testing Best Practices**:
     - Write tests that are independent and can run in parallel
     - Avoid dependencies on specific port numbers
     - Use meaningful container and network names for debugging
     - Consider using Docker Compose for complex setups
     - Use environment variables for configuration
