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
from testcontainers.core.generic import GenericContainer


class NginxContainer(GenericContainer):
    def __init__(self, image="nginx:latest", port_to_expose=80):
        super(NginxContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
