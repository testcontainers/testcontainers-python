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
import sqlalchemy

from testcontainers.core.docker_client import DockerClient
from testcontainers.core.waiting_utils import wait_container_is_ready


class Container(object):
    def __init__(self, image, version):
        self.env = {}
        self.ports = {}
        self._docker = DockerClient()
        self.image = "{}:{}".format(image, version)
        self._container = None

    def add_env(self, key, value):
        self.env[key] = value

    def expose_port(self, container, host):
        self.ports[container] = host

    def configure(self):
        raise NotImplementedError

    def start(self):
        self.configure()
        self._container = self._docker.run(self.image,
                                           detach=True,
                                           environment=self.env,
                                           ports=self.ports)
        return self

    def stop(self):
        self._container.remove(force=True)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_container_ip_address(self):
        pass

    def get_exposed_port(self, port):
        return self._docker.port(self._container.id, port)[0]["HostPort"]


class DbContainer(Container):
    def __init__(self,
                 image,
                 version,
                 dialect,
                 username,
                 password,
                 port,
                 db_name):
        super(DbContainer, self).__init__(image, version)
        self.dialect = dialect
        self.username = username
        self.password = password
        self.port = port
        self.db_name = db_name

    @wait_container_is_ready()
    def _connect(self):
        """
        dialect+driver://username:password@host:port/database
        :return:
        """
        engine = sqlalchemy.create_engine(self.get_connection_url())
        engine.connect()

    def get_connection_url(self):
        return "{lang}+pymysql://{username}" \
               ":{password}@{host}:" \
               "{port}/{db}".format(lang=self.dialect,
                                    username=self.username,
                                    password=self.password,
                                    host=self.get_container_ip_address(),
                                    port=self.get_exposed_port(self.port),
                                    db=self.db_name)

    def start(self):
        super().start()
        self._connect()
        return self


class MySqlContainer(DbContainer):
    def __init__(self, image="mysql", version="latest"):
        super(MySqlContainer, self).__init__(image,
                                             version,
                                             dialect="mysql",
                                             db_name="test",
                                             port="3306",
                                             username="test",
                                             password="test")
        self.root_password = "test"

    def configure(self):
        self.expose_port("3306/tcp", self.port)
        self.add_env("MYSQL_ROOT_PASSWORD", self.root_password)
        self.add_env("MYSQL_DATABASE", self.db_name)
        self.add_env("MYSQL_USER", self.username)
        self.add_env("MYSQL_PASSWORD", self.password)


# mysql = MySqlContainer().start()
#
# print(mysql._container.logs())
#
# print(mysql.get_exposed_port(3306))
#
# mysql.stop()
