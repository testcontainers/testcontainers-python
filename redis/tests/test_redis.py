import pytest

from testcontainers.redis import RedisContainer


@pytest.mark.parametrize('version', ['7.0.11', '6.2.12'])
def test_redis_container(version: str):
    image_name = f'redis:{version}'
    with RedisContainer(image_name, password="mypass") as redis:
        client = redis.get_client(decode_responses=True)
        client.set("hello", "world")
        assert client.get("hello") == "world"
