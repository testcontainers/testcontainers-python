from testcontainers_python import config
from testcontainers_python.docker_client import DockerClient


class MySqlContainer(object):
    def __init__(self, image='mysql:latest'):
        self._docker = DockerClient()
        self.image = image
        self._containers = []

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

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        for cont in self._containers:
            self._docker.remove(cont, True)
