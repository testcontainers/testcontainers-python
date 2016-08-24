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


from testcontainers.generic import GenericDbContainer


class PostgresDockerContainer(GenericDbContainer):
    host_port = 5432

    def __init__(self, version="latest"):
        super(PostgresDockerContainer, self).__init__()
        self._image_name = "postgres"
        self._version = version

    def _configure(self):
        self.add_env("POSTGRES_USER", self.user)
        self.add_env("POSTGRES_PASSWORD", self.passwd)
        self.add_env("POSTGRES_DB", self.user)
        self.bind_ports(self.host_port, 5432)
