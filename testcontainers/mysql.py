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


class MySqlDockerContainer(GenericDbContainer):
    def __init__(self, version="latest"):
        super(MySqlDockerContainer, self).__init__()
        self._image_name = "mysql"
        self._version = version

    def _configure(self):
        self.add_env("MYSQL_USER", self.user)
        self.add_env("MYSQL_PASSWORD", self.passwd)
        self.add_env("MYSQL_ROOT_PASSWORD", self.passwd)
        self.add_env("MYSQL_DATABASE", self.user)
        self.bind_ports(3306, 3306)
