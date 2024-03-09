import time

from testcontainers.redis import RedisContainer, AsyncRedisContainer
import pytest


def test_docker_run_redis():
    config = RedisContainer()
    with config as redis:
        client = redis.get_client()
        p = client.pubsub()
        p.subscribe("test")
        client.publish("test", "new_msg")
        msg = wait_for_message(p)
        assert "data" in msg
        assert b"new_msg", msg["data"]


def test_docker_run_redis_with_password():
    config = RedisContainer(password="mypass")
    with config as redis:
        client = redis.get_client(decode_responses=True)
        client.set("hello", "world")
        assert client.get("hello") == "world"


pytest.mark.usefixtures("anyio_backend")


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_key_set_in_async_redis(anyio_backend):
    with AsyncRedisContainer() as container:
        async_redis_client: redis.Redis = await container.get_async_client(decode_responses=True)
        key = "key"
        expected_value = 1
        await async_redis_client.set(key, expected_value)
        actual_value = await async_redis_client.get(key)
        assert int(actual_value) == expected_value


pytest.mark.usefixtures("anyio_backend")


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
@pytest.mark.skip(reason="Need to sort out async pub/sub")
async def test_docker_run_async_redis(anyio_backend):
    config = AsyncRedisContainer()
    with config as container:
        client: redis.Redis = await container.get_async_client(decode_responses=True)
        p = await client.pubsub()
        await p.subscribe("test")
        await client.publish("test", "new_msg")
        msg = wait_for_message(p)
        assert "data" in msg
        assert b"new_msg", msg["data"]


pytest.mark.usefixtures("anyio_backend")


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_docker_run_async_redis_with_password(anyio_backend):
    config = AsyncRedisContainer(password="mypass")
    with config as container:
        client: redis.Redis = await container.get_async_client(decode_responses=True)
        await client.set("hello", "world")
        assert await client.get("hello") == "world"


def wait_for_message(pubsub, timeout=1, ignore_subscribe_messages=True):
    now = time.time()
    timeout = now + timeout
    while now < timeout:
        message = pubsub.get_message(ignore_subscribe_messages=ignore_subscribe_messages)
        if message is not None:
            return message
        time.sleep(0.01)
        now = time.time()
    return None
