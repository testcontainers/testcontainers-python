import MySQLdb

from testcontainers_python import config
from testcontainers_python.generic_container import Container
from testcontainers_python.waiting_utils import wait_container_is_ready


class MySqlContainer(Container):
    def __init__(self, image='mysql:latest'):
        Container.__init__(self)
        self.image = image
        self.connection = None
        self._default_port = 3306

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        mysql = self._docker.run(self.image, **config.my_sql_container)
        self.connection = self._get_connection()
        self._containers.append(mysql)
        return self

    @wait_container_is_ready()
    def _get_connection(self):
        return MySQLdb.connect(**config.db)

    def stop(self):
        """
        Stop all spawned containers and close DB connection
        :return:
        """
        self.connection.close()
        Container.stop(self)
