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
import re
import string
from typing import Optional

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs

_UNSET = object()


class StarRocksContainer(DbContainer):
    """
    StarRocks database container.

    To get a URL without a driver, pass in :code:`driver=None`.

    Example:

        The example spins up a StarRocks database and connects to it using the :code:`pymysql`
        driver.

        .. doctest::

            >>> from testcontainers.starrocks import StarRocksContainer
            >>> import sqlalchemy

            >>> with StarRocksContainer("starrocks/allin1-ubuntu:3.5.3") as starrocks:
            ...     engine = sqlalchemy.create_engine(starrocks.get_connection_url())
            ...     with engine.begin() as connection:
            ...         result = connection.execute(sqlalchemy.text("select version()"))
            ...         version, = result.fetchone()
            >>> version
            'StarRocks...'
    """

    def __init__(
        self,
        image: str = "repo.smartech.ir/starrocks/allin1-ubuntu:3.5.3",
        dbname: string = "test",
        port: int = 9030,
        http_port: int = 8030,
        rpc_port: int = 9020,
        edit_log_port:int = 9010,
        heartbeat_port:int = 9050,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: Optional[str] = "pymysql",
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image=image, **kwargs)
        self.dbname: str = dbname
        self.username: str = username or os.environ.get("STARROCKS_USER", "root")
        self.password: str = password or os.environ.get("STARROCKS_PASSWORD", "")
        self.port = port
        self.http_port = http_port
        self.rpc_port = rpc_port
        self.edit_log_port = edit_log_port
        self.heartbeat_port = heartbeat_port
        self.driver = f"+{driver}" if driver else ""

        self.with_exposed_ports(self.port, self.http_port, self.rpc_port, self.edit_log_port, self.heartbeat_port)

    def _configure(self) -> None:
        self.with_env("STARROCKS_NODE_ROLE", "fe")
        self.with_env("FE_QUERY_PORT", str(self.port))
        self.with_env("FE_HTTP_PORT", str(self.http_port))
        self.with_env("FE_RPC_PORT", str(self.rpc_port))
        self.with_env("FE_EDIT_LOG_PORT", str(self.edit_log_port))
        self.with_env("STARROCKS_ROOT_PASSWORD", self.password)

    @wait_container_is_ready()
    def _connect(self) -> None:
        wait_for_logs(self,
                      re.compile(".*Enjoy the journey to StarRocks blazing-fast lake-house engine!.*", flags=re.DOTALL | re.MULTILINE).search,)
        
        # Create The Default Database If It Does Not Exist
        command = f'mysql -P 9030 -h 127.0.0.1 -u root -e "CREATE DATABASE IF NOT EXISTS {self.dbname}"'
        self.exec(command)

    def get_connection_url(self, host: Optional[str] = None, driver: Optional[str] = _UNSET) -> str:
        """Get a DB connection URL to connect to the StarRocks DB.

        If a driver is set in the constructor (defaults to pymysql), the URL will contain the
        driver. The optional driver argument to :code:`get_connection_url` overwrites the constructor
        set value. Pass :code:`driver=None` to get URLs without a driver.
        """
        driver_str = "" if driver is None else self.driver if driver is _UNSET else f"+{driver}"

        return super()._create_connection_url(
            dialect=f"mysql{driver_str}",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            host=host,
            port=self.port,
        )
