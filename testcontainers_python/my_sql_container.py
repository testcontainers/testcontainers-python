import MySQLdb

import context_manager
from testcontainers_python import config
from testcontainers_python.generic_container import GenericContainer


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
        mysql = self._docker.run(self.image, bind_ports={3306: 3306},
                                 env={"MYSQL_ROOT_PASSWORD": config.my_sql_root_password,
                                      "MYSQL_DATABASE": config.my_sql_db_name},
                                 name="mysql")
        self.connection = self._connect(mysql, 3306)
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
        Stop all spawned containers and close DB connection
        :return:
        """
        self.connection.close()
        GenericContainer.stop(self)
