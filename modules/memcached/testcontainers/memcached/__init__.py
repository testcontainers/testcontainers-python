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
import socket

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class MemcachedNotReady(Exception):
    pass


class MemcachedContainer(DockerContainer):
    """
    Test container for Memcached. The example below spins up a Memcached server

    Example:

        .. doctest::

            >>> from testcontainers.memcached import MemcachedContainer

            >>> with MemcachedContainer() as memcached_container:
            ...    host, port = memcached_container.get_host_and_port()
    """

    def __init__(self, image="memcached:1", port_to_expose=11211, **kwargs):
        super().__init__(image, **kwargs)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(port_to_expose)

    @wait_container_is_ready(MemcachedNotReady)
    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host = self.get_container_host_ip()
            port = int(self.get_exposed_port(self.port_to_expose))
            s.connect((host, port))
            s.sendall(b"stats\n\r")
            data = s.recv(1024)
            if len(data) == 0:
                raise MemcachedNotReady("Memcached not ready yet")

    def start(self):
        super().start()
        self._connect()
        return self

    def get_host_and_port(self):
        return self.get_container_host_ip(), int(self.get_exposed_port(self.port_to_expose))
