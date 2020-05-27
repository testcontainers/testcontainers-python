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
from os import environ

from testcontainers.core.generic import DbContainer


class MySqlContainer(DbContainer):
    """
    MySql database container.

    Example
    -------
    The example will spin up a MySql database to which you can connect with the credentials passed
    in the constructor. Alternatively, you may use the :code:`get_connection_url()` method which
    returns a sqlalchemy-compatible url in format
    :code:`dialect+driver://username:password@host:port/database`.
    ::

        with MySqlContainer('mysql:5.7.17') as mysql:
            e = sqlalchemy.create_engine(mysql.get_connection_url())
            result = e.execute("select version()")
            version, = result.fetchone()
    """
    MYSQL_USER = environ.get("MYSQL_USER", "test")
    MYSQL_ROOT_PASSWORD = environ.get("MYSQL_ROOT_PASSWORD", "test")
    MYSQL_PASSWORD = environ.get("MYSQL_PASSWORD", "test")
    MYSQL_DATABASE = environ.get("MYSQL_DATABASE", "test")

    def __init__(self, image="mysql:latest", **kwargs):
        super(MySqlContainer, self).__init__(image)
        self.port_to_expose = 3306
        self.with_exposed_ports(self.port_to_expose)
        if 'MYSQL_USER' in kwargs:
            self.MYSQL_USER = kwargs['MYSQL_USER']
        if 'MYSQL_ROOT_PASSWORD' in kwargs:
            self.MYSQL_ROOT_PASSWORD = kwargs['MYSQL_ROOT_PASSWORD']
        if 'MYSQL_PASSWORD' in kwargs:
            self.MYSQL_PASSWORD = kwargs['MYSQL_PASSWORD']
        if 'MYSQL_DATABASE' in kwargs:
            self.MYSQL_DATABASE = kwargs['MYSQL_DATABASE']

        if self.MYSQL_USER == 'root':
            self.MYSQL_ROOT_PASSWORD = self.MYSQL_PASSWORD

    def _configure(self):
        self.with_env("MYSQL_ROOT_PASSWORD", self.MYSQL_ROOT_PASSWORD)
        self.with_env("MYSQL_DATABASE", self.MYSQL_DATABASE)

        if self.MYSQL_USER != "root":
            self.with_env("MYSQL_USER", self.MYSQL_USER)
            self.with_env("MYSQL_PASSWORD", self.MYSQL_PASSWORD)

    def get_connection_url(self):
        return super()._create_connection_url(dialect="mysql+pymysql",
                                              username=self.MYSQL_USER,
                                              password=self.MYSQL_PASSWORD,
                                              db_name=self.MYSQL_DATABASE,
                                              port=self.port_to_expose)


class MariaDbContainer(MySqlContainer):
    """
    Maria database container, a commercially-supported fork of MySql.

    Example
    -------
    ::

        with MariaDbContainer("mariadb:latest") as mariadb:
            e = sqlalchemy.create_engine(mariadb.get_connection_url())
            result = e.execute("select version()")
    """
    def __init__(self, image="mariadb:latest", **kwargs):
        super(MariaDbContainer, self).__init__(image, **kwargs)
