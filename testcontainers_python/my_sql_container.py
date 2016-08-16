from time import sleep

from testcontainers_python import config
from testcontainers_python.brogress_bar import ConsoleProgressBar
from testcontainers_python.docker_client import DockerClient
import MySQLdb

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
                                 env={"MYSQL_ROOT_PASSWORD": config.my_sql_root_password})
        self._containers.append(mysql)
        self._connection = self._wait_for_container_to_start(mysql)
        return self

    def _wait_for_container_to_start(self, container):
        hub_info = self._docker.port(container, 3306)[0]
        bar = ConsoleProgressBar().bar
        for _ in bar(range(0, config.max_tries)):
            try:
                return MySQLdb.connect(host=hub_info['HostIp'],  # your host, usually localhost
                                       user="root",  # your username
                                       passwd=config.my_sql_root_password,  # your password
                                       db="test")
            except Exception:
                sleep(config.sleep_time)
        raise TimeoutException("Wait time exceeded {} sec.".format(config.max_tries))

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
