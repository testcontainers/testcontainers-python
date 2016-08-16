import logging
from time import sleep

from testcontainers_python import config
from testcontainers_python.brogress_bar import ConsoleProgressBar
from testcontainers_python.docker_client import DockerClient
import MySQLdb
import context_manager

from testcontainers_python.exceptions import TimeoutException


class MySqlContainer(object):
    def __init__(self, image='mysql:latest'):
        self._docker = DockerClient()
        self.image = image
        self._containers = []
        self._connection = None

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        """
        Start my sql container and wait to be ready
        :return:
        """
        mysql = self._docker.run(self.image, bind_ports={3306: 3306},
                                 env={"MYSQL_ROOT_PASSWORD": config.my_sql_root_password,
                                      "MYSQL_DATABASE": config.my_sql_db_name},
                                 name="mysql")
        self._connection = self._connect(mysql, 3306)
        self._containers.append(mysql)
        return self

    @context_manager.wait_container_is_ready()
    def _connect(self, container, port):
        hub_info = self._docker.port(container, port)[0]
        return MySQLdb.connect(host=hub_info['HostIp'],
                               user=config.my_sql_db_user,
                               passwd=config.my_sql_root_password,
                               db=config.my_sql_db_name)

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        self._connection.close()
        for cont in self._containers:
            self._docker.remove(cont, True)

    def get_connection(self):
        return self._connection
