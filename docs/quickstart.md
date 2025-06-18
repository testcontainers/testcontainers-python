_Testcontainers for Python_ integrates seamlessly with Python testing frameworks like [pytest](https://docs.pytest.org/en/stable/).

It's ideal for integration and end-to-end tests, allowing you to easily manage dependencies using Docker.

## 1. System requirements

Before you begin, review the [system requirements](system_requirements/index.md).

## 2. Install _Testcontainers for Python_

Install testcontainers-python with pip:

```bash
pip install testcontainers
```

## 3. Spin up Redis

```python
import pytest
from testcontainers.redis import RedisContainer
import redis

def test_with_redis():
    with RedisContainer() as redis_container:
        # Get connection parameters
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(redis_container.port)

        # Create Redis client
        client = redis.Redis(host=host, port=port, decode_responses=True)

        # Test Redis connection
        client.set("test_key", "Hello, Redis!")
        value = client.get("test_key")
        assert value == "Hello, Redis!"
```

The `RedisContainer` class makes it easy to start a Redis container for testing:

- The container starts automatically when entering the context manager (`with` statement).
- It stops and removes itself when exiting the context.
- `get_container_host_ip()` returns the host IP.
- `get_exposed_port()` returns the mapped host port.

When using `get_exposed_port()`, think of it as running `docker run -p <port>`. `dockerd` maps the container's internal port to a random available port on your host.

In the example above, the default Redis port (6379) is exposed for TCP traffic. This setup allows your code to connect to Redis outside the container and supports parallel test execution. Each test gets its own Redis container on a unique, random port.

The context manager (`with` statement) ensures containers are cleaned up after tests, so no containers are left running.

!!!tip

    See [the garbage collector](features/garbage_collector.md) for another way to clean up resources.

## 4. Connect your code to the container

Typically, Python applications use the [redis-py](https://github.com/redis/redis-py) client. The following code retrieves the endpoint from the container and configures the client.

```python
def test_redis_operations():
    with RedisContainer() as redis_container:
        # Get connection parameters
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(redis_container.port)

        # Create Redis client
        client = redis.Redis(host=host, port=port, decode_responses=True)

        # Test various Redis operations
        # String operations
        client.set("greeting", "Hello, Redis!")
        value = client.get("greeting")
        assert value == "Hello, Redis!"

        # List operations
        client.lpush("tasks", "task1", "task2", "task3")
        tasks = client.lrange("tasks", 0, -1)
        assert tasks == ["task3", "task2", "task1"]
```

## 5. Run the test

You can run the test via `pytest`:

```bash
pytest test_redis.py
```

## 6. Want to go deeper with Redis?

You can find a more elaborated Redis example in our [examples section](./modules/redis.md).
