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

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class DbContainer(DockerContainer):
    def __init__(self, image, dialect,
                 username,
                 password,
                 port,
                 db_name):
        super(DbContainer, self).__init__(image)
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
        return "{dialect}://{username}" \
               ":{password}@{host}:" \
               "{port}/{db}".format(dialect=self.dialect,
                                    username=self.username,
                                    password=self.password,
                                    host=self.get_container_host_ip(),
                                    port=self.get_exposed_port(self.port),
                                    db=self.db_name)

    def start(self):
        super().start()
        self._connect()
        return self

    def _configure(self):
        raise NotImplementedError


class GenericSeleniumContainer(DockerContainer):
    def __init__(self, image_name,
                 capabilities,
                 host_port,
                 container_port,
                 name,
                 host_vnc_port,
                 version="latest",
                 container_vnc_port=5900):
        super(GenericSeleniumContainer, self).__init__(image_name=image_name,
                                                       version=version,
                                                       container_name=name)
        self.host_port = host_port
        self.capabilities = capabilities
        self.container_port = container_port
        self.host_vnc_port = host_vnc_port
        self.container_vnc_port = container_vnc_port
        self._add_env()
        self.bind_ports(host_port, container_port)
        self.bind_ports(host_vnc_port, container_vnc_port)

    def _add_env(self):
        # this is workaround due to bug in Selenium images
        self.add_env("no_proxy", "localhost")
        self.add_env("HUB_ENV_no_proxy", "localhost")

    @wait_container_is_ready()
    def _connect(self):
        return webdriver.Remote(
            command_executor=(self.get_connection_url()),
            desired_capabilities=self.capabilities)

    def get_driver(self):
        return self._connect()

    def get_connection_url(self):
        ip = self.get_host_ip(self.container_port)
        port = self.get_host_port(self.container_port)
        return 'http://{}:{}/wd/hub'.format(ip, port)

    def _is_chrome(self):
        return self.capabilities["browserName"] == "chrome"
