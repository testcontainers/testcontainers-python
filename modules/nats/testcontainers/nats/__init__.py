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


# import asyncio
import typing

import nats
from nats.aio.client import Client as NATSClient
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class NatsContainer(DockerContainer):
    """
    Nats container.

    Example:

        .. doctest::

            >>> from testcontainers.nats import NatsContainer

            >>> with NatsContainer() as nats_container:
            ...     nc = nats_container.get_client()
    """

    def __init__(
        self,
        image: str = "nats:latest",
        client_port: int = 4222,
        manamgent_port: int = 8222,
        password: typing.Optional[str] = None,
        expected_ready_log: str = "Server is ready",
        ready_timeout_secs: int = 120,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.client_port = client_port
        self.management_port = manamgent_port
        self.password = password
        self._expected_ready_log = expected_ready_log
        self._ready_timeout_secs = max(ready_timeout_secs, 0)
        self.with_exposed_ports(self.client_port, self.management_port)

    @wait_container_is_ready()
    def _healthcheck(self) -> None:
        wait_for_logs(self, self._expected_ready_log, timeout=self._ready_timeout_secs)

    async def get_client(self, **kwargs) -> NATSClient:
        """
        Get a nats client.

        Args:
            **kwargs: Keyword arguments passed to `redis.Redis`.

        Returns:
            client: Nats client to connect to the container.
        """
        conn_string = f"nats://{self.get_container_host_ip()}:{self.get_exposed_port(self.client_port)}"
        client = await nats.connect(conn_string)
        return client

    def start(self) -> "NatsContainer":
        super().start()
        self._healthcheck()
        return self
