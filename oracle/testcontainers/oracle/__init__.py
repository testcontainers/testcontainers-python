from testcontainers.core.generic import DbContainer


class OracleDbContainer(DbContainer):
    """
    Oracle database container.

    Example:

        .. code-block::

            >>> import sqlalchemy
            >>> from testcontainers.oracle import OracleDbContainer

            >>> with OracleDbContainer() as oracle:
            ...     engine = sqlalchemy.create_engine(oracle.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("SELECT 1 FROM dual"))
    """

    def __init__(self, image: str = "gvenzl/oracle-free:slim", **kwargs) -> None:
        super(OracleDbContainer, self).__init__(image=image, **kwargs)
        self.container_port = 1521
        self.with_exposed_ports(self.container_port)

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect="oracle", username="system", password="oracle", port=self.container_port,
            dbname="freepdb1"
        )

    def _configure(self) -> None:
        pass
