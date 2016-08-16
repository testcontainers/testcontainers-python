import MySQLdb

from testcontainers_python import config
from testcontainers_python.generic_container import GenericContainer
from testcontainers_python.waiting_utils import wait_container_is_ready


class MySqlContainer(GenericContainer):
    def __init__(self, image='mysql:latest'):
        GenericContainer.__init__(self)
        self.image = image
        self.connection = None

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        mysql = self._docker.run(self.image, **config.my_sql_container)
        self.connection = self._connect(mysql, 3306)
        self._containers.append(mysql)
        return self

    @wait_container_is_ready()
    def _connect(self, container, port):
        hub_info = self._docker.port(container, port)[0]
        return MySQLdb.connect(host=hub_info['HostIp'], **config.db)

    def stop(self):
        """
        Stop all spawned containers and close DB connection
        :return:
        """
        self.connection.close()
        GenericContainer.stop(self)
