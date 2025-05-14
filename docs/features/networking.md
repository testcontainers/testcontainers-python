# Networking and Container Communication

Testcontainers-Python provides several ways to configure networking between containers and your test code. This is essential for testing distributed systems and microservices.

## Connection Modes

Testcontainers-Python supports three connection modes that determine how containers are accessed:

1. `bridge_ip` (default): Uses the bridge network IP address
2. `gateway_ip`: Uses the gateway IP address
3. `docker_host`: Uses the Docker host address

You can set the connection mode using the `TESTCONTAINERS_CONNECTION_MODE` environment variable or the `connection.mode` property in `.testcontainers.properties`.

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

## Port Mapping

You can map container ports to host ports:

```python
from testcontainers.core.container import DockerContainer

container = DockerContainer("nginx:alpine")
container.with_bind_ports(80, 8080)  # Map container port 80 to host port 8080
container.with_bind_ports("443/tcp", 8443)  # Map container port 443 to host port 8443
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

1. Use isolated networks for tests
2. Use meaningful network aliases
3. Avoid using host networking unless necessary
4. Use appropriate connection modes for your environment
5. Clean up networks after tests
6. Use port mapping for external access
7. Consider using Docker Compose for complex setups
8. Use environment variables for configuration
