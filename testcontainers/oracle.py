from testcontainers.core.generic import DbContainer


class OracleDbContainer(DbContainer):
    def __init__(self, image="wnameless/oracle-xe-11g:latest"):
        super(OracleDbContainer, self).__init__(image=image,
                                                username="system",
                                                password="oracle",
                                                db_name="xe",
                                                dialect="oracle",
                                                port=1521)
        self.host_port = 49161
        self.container_port = 1521
        self.host_ssh_port = 49160
        self.container_ssh_port = 22
        self.dialect = "oracle"

    def _configure(self):
        self.with_env("ORACLE_ALLOW_REMOTE", "true")
