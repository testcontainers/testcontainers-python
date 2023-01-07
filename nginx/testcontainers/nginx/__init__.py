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


class NginxContainer(DockerContainer):
    def __init__(self, image: str = "nginx:latest", port: int = 80, port_to_expose: None = None,
                 **kwargs) -> None:
        if port_to_expose:
            raise ValueError("use `port` instead of `port_to_expose`")
        super(NginxContainer, self).__init__(image, **kwargs)
        self.port = port
        self.with_exposed_ports(self.port)
