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


class MySqlContainer(GenericDbContainer):
    MYSQL_USER = "MYSQL_USER"
    MYSQL_PASSWORD = "MYSQL_PASSWORD"
    MYSQL_ROOT_PASSWORD = "MYSQL_ROOT_PASSWORD"
    MYSQL_DB_NAME = "MYSQL_DATABASE"
    _super_user_name = "root"

    def __init__(self, user,
                 password,
                 root_password="secret",
                 db="test",
                 host_port=3306,
                 image_name="mysql",
                 version="latest"):
        super(MySqlContainer, self).__init__(image_name=image_name,
                                             version=version,
                                             host_port=host_port,
                                             user=user,
                                             password=password,
                                             database=db,
                                             root_password=root_password)

    def _configure(self):
        if not self._is_root():
            self.config.add_env(self.MYSQL_USER, self.user)
            self.config.add_env(self.MYSQL_PASSWORD, self.passwd)
        self.config.add_env(self.MYSQL_ROOT_PASSWORD, self.root_password)
        self.config.add_env(self.MYSQL_DB_NAME, self.database)
        self.config.bind_ports(self.host_port, 3306)

    @property
    def username(self):
        if self._is_root():
            return self._super_user_name
        return self.get_env(self.MYSQL_USER)

    @property
    def password(self):
        if self._is_root():
            return self.get_env(self.MYSQL_ROOT_PASSWORD)
        return self.get_env(self.MYSQL_PASSWORD)

    @property
    def db(self):
        return self.get_env(self.MYSQL_DB_NAME)

    @property
    def host_ip(self):
        return "0.0.0.0"

    def _is_root(self):
        return self.user == self._super_user_name
