from testcontainers.core.generic import DbContainer


class OracleDbContainer(DbContainer):
    def __init__(self, image="wnameless/oracle-xe-11g-r2:latest"):
        super(OracleDbContainer, self).__init__(image=image)
        self.container_port = 1521
        self.with_exposed_ports(self.container_port)

    def _configure(self):
        self.with_env("ORACLE_ALLOW_REMOTE", "true")

    def get_connection_url(self):
        return super()._create_connection_url(dialect="oracle",
                                              username="system",
                                              password="oracle",
                                              port=self.container_port,
                                              db_name="xe")
