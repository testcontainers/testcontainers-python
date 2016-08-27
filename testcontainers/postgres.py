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

from testcontainers.core.generic import GenericDbContainer


class PostgresContainer(GenericDbContainer):
    def __init__(self, user,
                 passwd,
                 db="test",
                 host_port=5432,
                 image_name="postgres",
                 version="latest"):
        super(PostgresContainer, self).__init__(image_name=image_name,
                                                version=version,
                                                user=user,
                                                password=passwd,
                                                database=db,
                                                host_port=host_port,
                                                root_password=passwd)

        self.container_port = 5432

    def _configure(self):
        self._config.add_env("POSTGRES_USER", self.username)
        self._config.add_env("POSTGRES_PASSWORD", self.password)
        self._config.add_env("POSTGRES_DB", self.database)
        self._config.bind_ports(self.host_port, 5432)
