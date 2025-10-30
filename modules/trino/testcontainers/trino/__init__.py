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
import re

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.generic import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


class TrinoContainer(DockerContainer):
    def __init__(
        self,
        image="trinodb/trino:latest",
        user: str = "test",
        port: int = 8080,
        container_start_timeout: int = 30,
        **kwargs,
    ):
        super().__init__(image=image, **kwargs)
        self.user = user
        self.port = port
        self.with_exposed_ports(self.port)
        self.waiting_for(
            LogMessageWaitStrategy(re.compile(".*======== SERVER STARTED ========.*", re.MULTILINE))
            .with_poll_interval(c.sleep_time)
            .with_startup_timeout(container_start_timeout)
        )

    def get_connection_url(self):
        return f"trino://{self.user}@{self.get_container_host_ip()}:{self.port}"

    def _configure(self):
        pass
