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
from deprecation import deprecated
from testcontainers.core.container import DockerContainer


class TestContainer(DockerContainer):
    @deprecated(details="Use `DockerContainer`.")
    def __init__(self, image, port_to_expose=None):
        super(TestContainer, self).__init__(image)
        if port_to_expose:
            self.port_to_expose = port_to_expose
            self.with_exposed_ports(self.port_to_expose)
