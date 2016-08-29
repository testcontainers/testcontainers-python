from testcontainers.core.generic import GenericDbContainer


class OracleDbContainer(GenericDbContainer):
    def __init__(self, username="system", password="oracle", database="xe",
                 image_name="wnameless/oracle-xe-11g",
                 version="latest",
                 host_port=49161,
                 name="oracle-xe",
                 db_dialect="oracle"):
        super(OracleDbContainer, self).__init__(image_name=image_name,
                                                version=version,
                                                host_port=host_port,
                                                name=name,
                                                db_dialect=db_dialect,
                                                username=username,
                                                password=password,
                                                database=database)
        self.container_port = 1521
        self.host_ssh_port = 49160
        self.container_ssh_port = 22
        self._configure()

    def _configure(self):
        self.add_env("ORACLE_ALLOW_REMOTE", "true")
        self.bind_ports(self.host_port, self.container_port)
        self.bind_ports(self.host_ssh_port, self.container_ssh_port)
