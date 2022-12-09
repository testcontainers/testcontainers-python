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

import redis
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class RedisContainer(DockerContainer):
    """
        Redis container.

        Example
        -------
        .. doctest::

            >>> from testcontainers.redis import RedisContainer

            >>> with RedisContainer() as redis_container:
            ...     redis_client = redis_container.get_client()
        """
    def __init__(self, image="redis:latest", port_to_expose=6379, password=None, **kwargs):
        super(RedisContainer, self).__init__(image, **kwargs)
        self.port_to_expose = port_to_expose
        self.password = password
        self.with_exposed_ports(self.port_to_expose)
        if self.password:
            self.with_command(f"redis-server --requirepass {self.password}")

    @wait_container_is_ready(redis.exceptions.ConnectionError)
    def _connect(self):
        client = self.get_client()
        if not client.ping():
            raise redis.exceptions.ConnectionError("Could not connect to Redis")

    def get_client(self, **kwargs):
        """get redis client

        Parameters
        ----------
        kwargs: dict
            Keyword arguments passed to `redis.Redis`.

        Returns
        -------
        client: redis.Redis
            Redis client to connect to the container.
        """
        return redis.Redis(
            host=self.get_container_host_ip(),
            port=self.get_exposed_port(self.port_to_expose),
            password=self.password,
            **kwargs,
        )

    def start(self):
        super().start()
        self._connect()
        return self
