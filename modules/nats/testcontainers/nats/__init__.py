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


from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class NatsContainer(DockerContainer):
    """
    Nats container.

    Example:

        .. doctest::

            >>> import asyncio
            >>> from nats import connect as nats_connect
            >>> from testcontainers.nats import NatsContainer

            >>> async def test_doctest_usage():
            ...     with NatsContainer() as nats_container:
            ...         client = await nats_connect(nats_container.nats_uri())
            ...         sub_tc = await client.subscribe("tc")
            ...         await client.publish("tc", b"Test-Containers")
            ...         next_message = await sub_tc.next_msg(timeout=5.0)
            ...         await client.close()
            ...     return next_message.data
            >>> asyncio.run(test_doctest_usage())
            b'Test-Containers'
    """

    def __init__(
        self,
        image: str = "nats:latest",
        client_port: int = 4222,
        management_port: int = 8222,
        expected_ready_log: str = "Server is ready",
        ready_timeout_secs: int = 120,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.client_port = client_port
        self.management_port = management_port
        self._expected_ready_log = expected_ready_log
        self._ready_timeout_secs = max(ready_timeout_secs, 0)
        self.with_exposed_ports(self.client_port, self.management_port)

    @wait_container_is_ready()
    def _healthcheck(self) -> None:
        wait_for_logs(self, self._expected_ready_log, timeout=self._ready_timeout_secs)

    def nats_uri(self) -> str:
        return f"nats://{self.get_container_host_ip()}:{self.get_exposed_port(self.client_port)}"

    def nats_host_and_port(self) -> tuple[str, int]:
        return self.get_container_host_ip(), self.get_exposed_port(self.client_port)

    def nats_management_uri(self) -> str:
        return f"nats://{self.get_container_host_ip()}:{self.get_exposed_port(self.management_port)}"

    def start(self) -> "NatsContainer":
        super().start()
        self._healthcheck()
        return self
