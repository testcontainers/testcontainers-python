#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from typing import Optional

import redis
from redis.asyncio import Redis as asyncRedis
from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class RedisContainer(DockerContainer):
    """
    Redis container.

    Example:

        .. doctest::

            >>> from testcontainers.redis import RedisContainer

            >>> with RedisContainer() as redis_container:
            ...     redis_client = redis_container.get_client()
    """

    def __init__(self, image: str = "redis:latest", port: int = 6379, password: Optional[str] = None, **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.password = password
        self.with_exposed_ports(self.port)
        if self.password:
            self.with_command(f"redis-server --requirepass {self.password}")

    @wait_container_is_ready(redis.exceptions.ConnectionError)
    def _connect(self) -> None:
        client = self.get_client()
        if not client.ping():
            raise redis.exceptions.ConnectionError("Could not connect to Redis")

    def get_client(self, **kwargs) -> redis.Redis:
        """
        Get a redis client.

        Args:
            **kwargs: Keyword arguments passed to `redis.Redis`.

        Returns:
            client: Redis client to connect to the container.
        """
        return redis.Redis(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port),
            password=self.password,
            **kwargs,
        )

    def start(self) -> "RedisContainer":
        super().start()
        self._connect()
        return self


class AsyncRedisContainer(RedisContainer):
    """
    Redis container.

    Example
    -------
    .. doctest::

        >>> from testcontainers.redis import AsyncRedisContainer

        >>> with AsyncRedisContainer() as redis_container:
        ...     redis_client =await  redis_container.get_async_client()
    """

    def __init__(self, image="redis:latest", port_to_expose=6379, password=None, **kwargs):
        super().__init__(image, port_to_expose, password, **kwargs)

    async def get_async_client(self, **kwargs):
        return await asyncRedis(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port),
            password=self.password,
            **kwargs,
        )
