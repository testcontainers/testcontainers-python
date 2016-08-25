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
from testcontainers.core.config import DbConfig

from testcontainers.core.generic import GenericDbContainer


class PostgresDockerContainer(GenericDbContainer):
    def __init__(self, config):
        super(PostgresDockerContainer, self).__init__(config)


class PostgresConfig(DbConfig):
    POSTGRES_USER = "POSTGRES_USER"
    POSTGRES_PASSWORD = "POSTGRES_PASSWORD"
    POSTGRES_DB = "POSTGRES_DB"

    def __init__(self, user, passwd,
                 db="test", host_port=5432, image="postgres", version="latest"):
        super(PostgresConfig, self).__init__(image, version=version)
        self.add_env(self.POSTGRES_USER, user)
        self.add_env(self.POSTGRES_PASSWORD, passwd)
        self.add_env(self.POSTGRES_DB, db)
        self.bind_ports(host_port, 5432)

    @property
    def db(self):
        return self.env[self.POSTGRES_DB]

    @property
    def password(self):
        return self.env[self.POSTGRES_PASSWORD]

    @property
    def username(self):
        return self.env[self.POSTGRES_USER]
