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
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_for_logs


class NginxContainer(DockerContainer):
    def __init__(self, image: str = "nginx:latest", port: int = 80, **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.with_exposed_ports(self.port)

    def start(self) -> DockerContainer:
        container = super().start()
        wait_for_logs(container, 'ready for start up')
        return container
