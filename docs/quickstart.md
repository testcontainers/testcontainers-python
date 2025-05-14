_Testcontainers for Python_ plays well with Python's testing frameworks like pytest.

The ideal use case is for integration or end to end tests. It helps you to spin
up and manage the dependencies life cycle via Docker.

## 1. System requirements

Please read the [system requirements](../system_requirements) page before you start.

## 2. Install _Testcontainers for Python_

You can install testcontainers-python using pip:

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

The `RedisContainer` class provides a convenient way to start a Redis container for testing.

- The container is automatically started when entering the context manager (`with` statement)
- The container is automatically stopped and removed when exiting the context manager
- `get_container_host_ip()` returns the host IP where the container is running
- `get_exposed_port()` returns the mapped port on the host

When you use `get_exposed_port()`, you have to imagine yourself using `docker run -p
<port>`. When you do so, `dockerd` maps the selected `<port>` from inside the
container to a random one available on your host.

In the previous example, we expose the default Redis port (6379) for `tcp` traffic to the outside. This
allows Redis to be reachable from your code that runs outside the container, but
it also makes parallelization possible because if you run your tests in parallel, each test will get its own Redis container exposed on a different random port.

The container is automatically cleaned up when the test finishes, thanks to the context manager (`with` statement). This ensures that no containers are left running after your tests complete.

!!!tip

    Look at [features/garbage_collector](/features/garbage_collector) to know another way to
    clean up resources.

## 4. Make your code to talk with the container

This is just an example, but usually Python applications that rely on Redis are
using the [redis-py](https://github.com/redis/redis-py) client. This code gets
the endpoint from the container we just started, and it configures the client.

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

You can find a more elaborated Redis example in our examples section. Please check it out [here](./modules/redis.md).
