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
        self.ENV_POSTGRES_USER = "POSTGRES_USER"
        self.ENV_POSTGRES_PASSWORD = "POSTGRES_PASSWORD"
        self.ENV_POSTGRES_DB = "POSTGRES_DB"

    def _configure(self):
        self.add_env(self.ENV_POSTGRES_USER, self.user)
        self.add_env(self.ENV_POSTGRES_PASSWORD, self.passwd)
        self.add_env(self.ENV_POSTGRES_DB, self.database)
        self.config.bind_ports(self.host_port, 5432)

    @property
    def db(self):
        return self.get_env(self.ENV_POSTGRES_DB)

    @property
    def password(self):
        return self.get_env(self.ENV_POSTGRES_PASSWORD)

    @property
    def username(self):
        return self.get_env(self.ENV_POSTGRES_USER)

    @property
    def host_ip(self):
        return "0.0.0.0"
