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
import redis as redis

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class RedisContainer(DockerContainer):
    def __init__(self, image="redis:latest", port_to_expose=6379):
        super(RedisContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)

    @wait_container_is_ready()
    def _connect(self):
        client = self.get_client()
        if not client.ping():
            raise Exception

    def get_client(self):
        return redis.Redis(host=self.get_container_host_ip(), port=self.get_exposed_port(6379))

    def start(self):
        super().start()
        self._connect()
        return self
