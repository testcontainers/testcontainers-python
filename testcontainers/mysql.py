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


class MySqlDockerContainer(GenericDbContainer):
    def __init__(self, config):
        super(MySqlDockerContainer, self).__init__(config)


class MySqlConfig(DbConfig):
    MYSQL_USER = "MYSQL_USER"
    MYSQL_PASSWORD = "MYSQL_PASSWORD"
    MYSQL_ROOT_PASSWORD = "MYSQL_ROOT_PASSWORD"
    MYSQL_DB_NAME = "MYSQL_DATABASE"
    _super_user_name = "root"

    def __init__(self, user, password, superuser=False, root_pass="secret",
                 db="test", host_port=3306, image="mysql", version="latest"):
        super(MySqlConfig, self).__init__(image, version)
        self.superuser = superuser
        if not superuser:
            self.add_env(self.MYSQL_USER, user)
            self.add_env(self.MYSQL_PASSWORD, password)
        self.add_env(self.MYSQL_ROOT_PASSWORD, root_pass)
        self.add_env(self.MYSQL_DB_NAME, db)
        self.bind_ports(host_port, 3306)

    @property
    def username(self):
        if self.superuser:
            return self._super_user_name
        return self.env[self.MYSQL_USER]

    @property
    def password(self):
        if self.superuser:
            return self.env[self.MYSQL_ROOT_PASSWORD]
        return self.env[self.MYSQL_PASSWORD]

    @property
    def db(self):
        return self.env[self.MYSQL_DB_NAME]
