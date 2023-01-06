"""
ArangoDB container support.
"""
from os import environ
from testcontainers.core.config import MAX_TRIES
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_for_logs
import typing


class ArangoDbContainer(DbContainer):
    """
    ArangoDB container.

    Example
    -------
    The example will spin up a ArangoDB container.
    You may use the :code:`get_connection_url()` method which returns a arangoclient-compatible url
    in format :code:`scheme://host:port`. As of now, only a single host is supported (over HTTP).

    .. doctest::

        >>> from testcontainers.arangodb import ArangoDbContainer
        >>> from arango import ArangoClient

        >>> with ArangoDbContainer("arangodb:3.9.1") as arango:
        ...    client = ArangoClient(hosts=arango.get_connection_url())
        ...
        ...    # Connect
        ...    sys_db = client.db(username="root", password="passwd")
        ...
        ...    # Create a new database named "test".
        ...    sys_db.create_database("test")
        True
    """

    def __init__(self,
                 image: str = "arangodb:latest",
                 port_to_expose: int = 8529,
                 arango_root_password: str = "passwd",
                 arango_no_auth: typing.Optional[bool] = None,
                 arango_random_root_password: typing.Optional[bool] = None,
                 **kwargs):
        """
        Args:
            image: Actual docker image/tag to pull.
            port_to_expose: Port the container needs to expose.
            arango_root_password: Start ArangoDB with the given password for root. Defaults to the
                environment variable `ARANGO_ROOT_PASSWORD` if `None`.
            arango_no_auth: Disable authentication completely. Defaults to the environment variable
                `ARANGO_NO_AUTH` if `None` or `False` if the environment variable is not available.
            arango_random_root_password: Let ArangoDB generate a random root password. Defaults to
                the environment variable `ARANGO_NO_AUTH` if `None` or `False` if the environment
                variable is not available.
        """
        super().__init__(image=image, **kwargs)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)

        # See https://www.arangodb.com/docs/stable/deployment-single-instance-manual-start.html for
        # details. We convert to int then to bool because Arango uses the string literal "1" to
        # indicate flags.
        self.arango_no_auth = bool(int(environ.get("ARANGO_NO_AUTH", 0) if arango_no_auth is None
                                   else arango_no_auth))
        self.arango_root_password = environ.get("ARANGO_ROOT_PASSWORD") if arango_root_password is \
            None else arango_root_password
        self.arango_random_root_password = bool(int(
            environ.get("ARANGO_RANDOM_ROOT_PASSWORD", 0) if arango_random_root_password is None
            else arango_random_root_password
        ))

    def _configure(self):
        self.with_env("ARANGO_ROOT_PASSWORD", self.arango_root_password)
        if self.arango_no_auth:
            self.with_env("ARANGO_NO_AUTH", "1")
        if self.arango_random_root_password:
            self.with_env("ARANGO_RANDOM_ROOT_PASSWORD", "1")

    def get_connection_url(self):
        # for now, single host over HTTP
        scheme = "http"
        port = self.get_exposed_port(self.port_to_expose)
        url = f"{scheme}://{self.get_container_host_ip()}:{port}"

        return url

    def _connect(self):
        wait_for_logs(
            self,
            predicate="is ready for business",
            timeout=MAX_TRIES)
