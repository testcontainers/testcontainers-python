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
from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

if TYPE_CHECKING:
    from typing_extensions import Self

    from testcontainers.core.network import Network
    from testcontainers.mssql import SqlServerContainer

    from ._types import ServiceBusConfiguration

log = logging.getLogger(__name__)


class ServiceBusContainer(DockerContainer):
    """
    CockroachDB database container.

    Example:

        The example will spin up a ServiceBus broker to which you can connect with the credentials
        passed in the constructor. Alternatively, you may use the :code:`get_connection_url()`
        method which returns a ServiceBusClient compatible url.

        .. doctest::

            >>> from azure.servicebus import ServiceBusClient
            >>> from testcontainers.azure import ServiceBusContainer
            >>> from testcontainers.mssql import SqlServerContainer
            >>> from testcontainers.core.network import Network

            >>> CONFIG = {"UserConfig":{"Namespaces":[{"Name":"namespace","Queues":[],"Topics":[
            ... {"Name":"topic","Properties":{},"Subscriptions":[]}]}],"Logging":{"Type":"File"}}}
            >>> network = Network().create()
            >>> with SqlServerContainer().with_network(network) as mssql_container:
            ...     with ServiceBusContainer(
            ...         config=CONFIG, network=network, mssql_container=mssql_container
            ...     ) as sb_container:
            ...         client = ServiceBusClient.from_connection_string(
            ...             sb_container.get_connection_url(), logging_enable=True
            ...         )
            ...         with client.get_topic_sender(topic_name="topic") as sender:
            ...             sender.send_messages(ServiceBusMessage("test"))

    """

    CONNECTION_STRING_FORMAT = (
        "Endpoint=sb://{}:{};SharedAccessKeyName=RootManageSharedAccessKey;"
        "SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
    )

    def __init__(
        self,
        *,
        config: ServiceBusConfiguration,
        network: Network,
        mssql_container: SqlServerContainer,
        port: int = 5672,
        image: str = "mcr.microsoft.com/azure-messaging/servicebus-emulator:latest",
        mssql_container_wait: int = 0,
    ):
        self.config = config
        self.network = network
        self.port = port
        self.image = image

        self._mssql_container = mssql_container
        self._mssql_container_wait = mssql_container_wait

        # Create a temporary config file for the emulator
        self._configdir = tempfile.TemporaryDirectory()
        log.debug("Using %r as a configuration directory.", self._configdir.name)
        with open(str(Path(self._configdir.name) / "Config.json"), "w") as f:
            f.write(json.dumps(config))

        # Configure.
        super().__init__(self.image)
        self.with_volume_mapping(self._configdir.name, "/ServiceBus_Emulator/ConfigFiles", mode="ro").with_env(
            "SQL_SERVER", "sql"
        ).with_env("MSSQL_SA_PASSWORD", mssql_container.password).with_network_aliases("servicebus").with_exposed_ports(
            self.port
        ).with_network(network).with_env("SQL_WAIT_INTERVAL", str(self._mssql_container_wait))

    def accept_license(self) -> Self:
        """Accept the Microsoft EULA for the service bus emulator.

        Required for startup to succeed."""
        self.with_env("ACCEPT_EULA", "Y")
        return self

    def _connect(self) -> None:
        wait_for_logs(self, "Emulator Service is Successfully Up!", timeout=15)

    def start(self) -> Self:
        # Make the sql container accessible from ServiceBus.
        self._mssql_container.with_network_aliases("sql").start()
        super().start()
        self._connect()
        return self

    def get_connection_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)

        return self.CONNECTION_STRING_FORMAT.format(host, port)
