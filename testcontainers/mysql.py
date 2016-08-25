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
from testcontainers.config import ContainerConfig
from testcontainers.generic import GenericDbContainer


class MySqlDockerContainer(GenericDbContainer):
    def __init__(self, config):
        super(MySqlDockerContainer, self).__init__(config)

    @property
    def password(self):
        return self.config.password

    @property
    def username(self):
        return self.config.username

    @property
    def db(self):
        return self.config.db


class MySqlConfig(ContainerConfig):
    mysql_user = "MYSQL_USER"
    mysql_password = "MYSQL_PASSWORD"
    mysql_root_password = "MYSQL_ROOT_PASSWORD"
    mysql_db_name = "MYSQL_DATABASE"
    _super_user_name = "root"

    def __init__(self, user, password, superuser=False, root_pass="secret",
                 db="test", host_port=3306, image="mysql", version="latest"):
        super(MySqlConfig, self).__init__(image, version)
        self.superuser = superuser
        if not superuser:
            self.add_env(self.mysql_user, user)
            self.add_env(self.mysql_password, password)
        self.add_env(self.mysql_root_password, root_pass)
        self.add_env(self.mysql_db_name, db)
        self.bind_ports(host_port, 3306)

    @property
    def username(self):
        if self.superuser:
            return self._super_user_name
        return self.env[self.mysql_user]

    @property
    def password(self):
        if self.superuser:
            return self.env[self.mysql_root_password]
        return self.env[self.mysql_password]

    @property
    def db(self):
        return self.env[self.mysql_db_name]
