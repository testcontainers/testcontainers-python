from os import environ
from typing import Optional
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

    def __init__(self, image: str = "gvenzl/oracle-free:slim",
                 oracle_password: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None,
                 port: int = 1521, dbname: Optional[str] = None, **kwargs) -> None:
        super(OracleDbContainer, self).__init__(image=image, **kwargs)

        self.port = port
        self.with_exposed_ports((self.port,))

        self.oracle_password = oracle_password or environ.get("ORACLE_PASSWORD")
        self.username = username or environ.get("APP_USER")
        self.password = password or environ.get("APP_USER_PASSWORD")
        self.dbname = dbname or environ.get("ORACLE_DATABASE")

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect="oracle+oracledb",
            username=self.username or "system", password=self.password or self.oracle_password,
            port=self.port, dbname=self.dbname
        )

    def _configure(self) -> None:
        if self.oracle_password is not None:
            self.with_env("ORACLE_PASSWORD", self.oracle_password)
        else:
            self.with_env("ORACLE_RANDOM_PASSWORD", "y")

        if self.username is not None:
            self.with_env("APP_USER", self.username)
        if self.password is not None:
            self.with_env("APP_USER_PASSWORD", self.password)
        if self.dbname is not None:
            self.with_env("ORACLE_DATABASE", self.dbname)