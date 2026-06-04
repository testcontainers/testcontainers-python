from os import environ
from secrets import randbits
from typing import Optional

from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_for_logs


class OracleDbContainer(DbContainer):
    """
    Oracle database container.

    Example:

        .. doctest::

            >>> import sys, pytest
            >>> if sys.platform.startswith('win') or sys.platform == 'darwin':
            ...     pytest.skip("linux only test")

            >>> import sqlalchemy
            >>> from testcontainers.oracle import OracleDbContainer

            >>> with OracleDbContainer() as oracle:
            ...     engine = sqlalchemy.create_engine(oracle.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("SELECT 1 FROM dual"))
            ...         result.fetchall()
            [(1,)]
    """

    def __init__(
        self,
        image: str = "gvenzl/oracle-free:slim",
        oracle_password: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 1521,
        dbname: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

        self.oracle_password = oracle_password or environ.get("ORACLE_PASSWORD") or hex(randbits(24))
        self.username = username or environ.get("APP_USER")
        self.password = password or environ.get("APP_USER_PASSWORD")
        self.dbname = dbname or environ.get("ORACLE_DATABASE")

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect="oracle+oracledb",
            username=self.username or "system",
            password=self.password or self.oracle_password,
            port=self.port,
        ) + "/?service_name={}".format(self.dbname or "FREEPDB1")
        # Default DB is "FREEPDB1"

    def _connect(self) -> None:
        wait_for_logs(self, "DATABASE IS READY TO USE!")

    def _configure(self) -> None:
        # if self.oracle_password is not None:
        #     self.with_env("ORACLE_PASSWORD", self.oracle_password)
        # # Either ORACLE_PASSWORD or ORACLE_RANDOM_PASSWORD need to be passed on
        # else:
        #     self.with_env("ORACLE_RANDOM_PASSWORD", "y")
        # this module is unusable with a random password
        self.with_env("ORACLE_PASSWORD", self.oracle_password)

        if self.username is not None:
            self.with_env("APP_USER", self.username)
        if self.password is not None:
            self.with_env("APP_USER_PASSWORD", self.password)

        # FREE and FREEPDB1 are predefined databases, do not pass them on as ORACLE_DATABASE
        if self.dbname is not None and self.dbname.upper() not in ("FREE", "FREEPDB1"):
            self.with_env("ORACLE_DATABASE", self.dbname)
