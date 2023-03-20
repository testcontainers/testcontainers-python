#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os
from typing import Optional
from testcontainers.core.generic import DbContainer

class Db2Container(DbContainer):
    """
    IBM Db2 database container.

    Example:

            >>> import sqlalchemy
            >>> from testcontainers.db2 import Db2Container
            >>> from testcontainers.core.waiting_utils import wait_for_logs
            >>> with Db2Container() as db2:
            >>>     wait_for_logs(db2, "(*) Setup has completed")
            ...     engine = sqlalchemy.create_engine(db2.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("SELECT SERVICE_LEVEL FROM SYSIBMADM.ENV_INST_INFO"))
            ...         version, = result.fetchone()
    """
    DB2_USER = os.environ.get("DB2_USER", "test")
    DB2_PASSWORD = os.environ.get("DB2_PASSWORD", "test")
    DB2_DATABASE = os.environ.get("DB2_DATABASE", "test")

    def __init__(
        self, 
        image: str = "ibmcom/db2:latest", 
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None, 
        port: int = 50_000, 
        **kwargs
    ) -> None:
        super(Db2Container, self).__init__(image=image, **kwargs)
        self.DB2_USER = user or self.DB2_USER
        self.DB2_PASSWORD = password or self.DB2_PASSWORD
        self.DB2_DATABASE = database or self.DB2_DATABASE
        self.port_to_expose = port

        self.with_exposed_ports(self.port_to_expose)

    def _configure(self) -> None:
        self.with_env("DB2INSTANCE", self.DB2_USER)
        self.with_env("DB2INST1_PASSWORD", self.DB2_PASSWORD)
        self.with_env("DBNAME", self.DB2_DATABASE)
        self.with_env("LICENSE", "accept")
        # the following settings reduce container start-up time
        self.with_env("ARCHIVE_LOGS", "false")
        self.with_env("AUTOCONFIG", "false")

    def get_connection_url(self, host=None) -> str:
        return super()._create_connection_url(
            dialect="db2", 
            username=self.DB2_USER, 
            password=self.DB2_PASSWORD, 
            db_name=self.DB2_DATABASE, 
            host=host,
            port=self.port_to_expose,
        )
