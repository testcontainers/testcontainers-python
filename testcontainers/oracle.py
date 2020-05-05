from testcontainers.core.generic import DbContainer


class OracleDbContainer(DbContainer):
    """
    Oracle database container.

    Example
    -------
    ::

        with OracleDbContainer():
            e = sqlalchemy.create_engine(oracle.get_connection_url())
            result = e.execute("select 1 from dual")
    """
    def __init__(self, image="wnameless/oracle-xe-11g-r2:latest"):
        super(OracleDbContainer, self).__init__(image=image)
        self.container_port = 1521
        self.with_exposed_ports(self.container_port)
        self.with_env("ORACLE_ALLOW_REMOTE", "true")

    def get_connection_url(self):
        return super()._create_connection_url(
            dialect="oracle", username="system", password="oracle", port=self.container_port,
            db_name="xe"
        )
