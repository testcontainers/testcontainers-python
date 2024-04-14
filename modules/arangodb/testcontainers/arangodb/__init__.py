"""
ArangoDB container support.
"""

import typing
from os import environ

from testcontainers.core.config import testcontainers_config as c
from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_for_logs


class ArangoDbContainer(DbContainer):
    """
    ArangoDB container.

    Example:

        This example spins up an ArangoDB container. You may use the :code:`get_connection_url()`
        method which returns a arangoclient-compatible url in format :code:`scheme://host:port`. As
        of now, only a single host is supported (over HTTP).

        .. doctest::

            >>> from testcontainers.arangodb import ArangoDbContainer
            >>> from arango import ArangoClient

            >>> with ArangoDbContainer("arangodb:3.11.8") as arango:
            ...    client = ArangoClient(hosts=arango.get_connection_url())
            ...
            ...    # Connect
            ...    sys_db = client.db(username="root", password="passwd")
            ...
            ...    # Create a new database named "test".
            ...    sys_db.create_database("test")
            True
    """

    def __init__(
        self,
        image: str = "arangodb:latest",
        port: int = 8529,
        arango_root_password: str = "passwd",
        arango_no_auth: typing.Optional[bool] = None,
        arango_random_root_password: typing.Optional[bool] = None,
        **kwargs,
    ) -> None:
        """
        Args:
            image: Actual docker image/tag to pull.
            port: Port the container needs to expose.
            arango_root_password: Start ArangoDB with the given password for root. Defaults to the
                environment variable `ARANGO_ROOT_PASSWORD` if `None`.
            arango_no_auth: Disable authentication completely. Defaults to the environment variable
                `ARANGO_NO_AUTH` if `None` or `False` if the environment variable is not available.
            arango_random_root_password: Let ArangoDB generate a random root password. Defaults to
                the environment variable `ARANGO_NO_AUTH` if `None` or `False` if the environment
                variable is not available.
        """
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image=image, **kwargs)
        self.port = port
        self.with_exposed_ports(self.port)

        # See https://www.arangodb.com/docs/stable/deployment-single-instance-manual-start.html for
        # details. We convert to int then to bool because Arango uses the string literal "1" to
        # indicate flags.
        self.arango_no_auth = bool(int(environ.get("ARANGO_NO_AUTH", 0) if arango_no_auth is None else arango_no_auth))
        self.arango_root_password = (
            environ.get("ARANGO_ROOT_PASSWORD") if arango_root_password is None else arango_root_password
        )
        self.arango_random_root_password = bool(
            int(
                environ.get("ARANGO_RANDOM_ROOT_PASSWORD", 0)
                if arango_random_root_password is None
                else arango_random_root_password
            )
        )

    def _configure(self) -> None:
        self.with_env("ARANGO_ROOT_PASSWORD", self.arango_root_password)
        if self.arango_no_auth:
            self.with_env("ARANGO_NO_AUTH", "1")
        if self.arango_random_root_password:
            self.with_env("ARANGO_RANDOM_ROOT_PASSWORD", "1")

    def get_connection_url(self) -> str:
        port = self.get_exposed_port(self.port)
        return f"http://{self.get_container_host_ip()}:{port}"

    def _connect(self) -> None:
        wait_for_logs(self, predicate="is ready for business", timeout=c.timeout)
