from os import environ
from typing import Optional

from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class Db2Container(DbContainer):
    """
    IBM Db2 database container.

    Example:

        .. doctest::

            >>> import sqlalchemy
            >>> from testcontainers.db2 import Db2Container

            >>> with Db2Container("icr.io/db2_community/db2:latest") as db2:
            ...    engine = sqlalchemy.create_engine(db2.get_connection_url())
            ...    with engine.begin() as connection:
            ...        result = connection.execute(sqlalchemy.text("select service_level from sysibmadm.env_inst_info"))
    """

    def __init__(
        self,
        image: str = "icr.io/db2_community/db2:latest",
        username: str = "db2inst1",
        password: Optional[str] = None,
        port: int = 50000,
        dbname: str = "testdb",
        dialect: str = "db2+ibm_db",
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)

        self.port = port
        self.with_exposed_ports(self.port)

        self.password = password or environ.get("DB2_PASSWORD", "password")
        self.username = username
        self.dbname = dbname
        self.dialect = dialect

    def _configure(self) -> None:
        self.with_env("LICENSE", "accept")
        self.with_env("DB2INSTANCE", self.username)
        self.with_env("DB2INST1_PASSWORD", self.password)
        self.with_env("DBNAME", self.dbname)
        self.with_env("ARCHIVE_LOGS", "false")
        self.with_env("AUTOCONFIG", "false")
        self.with_kwargs(privileged=True)

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self, predicate="Setup has completed")

    def get_connection_url(self) -> str:
        return super()._create_connection_url(
            dialect=self.dialect, username=self.username, password=self.password, dbname=self.dbname, port=self.port
        )
