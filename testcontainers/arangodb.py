"""
ArangoDB container support.
"""
from os import environ
from testcontainers.core.config import MAX_TRIES
from testcontainers.core.generic import DbContainer
from testcontainers.core.waiting_utils import wait_for_logs


class ArangoDbContainer(DbContainer):
    """
    ArangoDB container.

    Example
    -------
    The example will spin up a ArangoDB container.
    You may use the :code:`get_connection_url()` method which returns a arangoclient-compatible url
    in format :code:`scheme://host:port`. As of now, only a single host is supported (over HTTP).
    ::

        with ArangoContainer("arangodb:3.9.1") as arango:
            client = ArangoClient(hosts=arango.get_connection_url())

            # Connect
            sys_db = arango_client.db(username='root', password='')

            # Create a new database named "test".
            sys_db.create_database("test")
    """
    def __init__(self,
                 image="arangodb:latest",
                 port_to_expose=8529,
                 arango_root_password='passwd',
                 arango_no_auth=False,
                 arango_random_root_password=False,
                 **kwargs):
        """
        Args:
            image (str, optional): Actual docker image/tag to pull. Defaults to "arangodb:latest".
            port_to_expose (int, optional): Port the container needs to expose. Defaults to 8529.
            arango_root_password (str, optional): Start ArangoDB with the
                given password for root. Defaults to 'passwd'.
            arango_no_auth (bool, optional): Disable authentication completely.
                Defaults to False.
            arango_random_root_password (bool, optional): Let ArangoDB generate a
                random root password. Defaults to False.
        """
        super().__init__(image=image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)

        # https://www.arangodb.com/docs/stable/deployment-single-instance-manual-start.html
        self.arango_no_auth = arango_no_auth or \
            environ.get("ARANGO_NO_AUTH")
        self.arango_root_password = arango_root_password or \
            environ.get('ARANGO_ROOT_PASSWORD')
        self.arango_random_root_password = arango_random_root_password or \
            environ.get('ARANGO_RANDOM_ROOT_PASSWORD')

    def _configure(self):
        self.with_env(
            "ARANGO_NO_AUTH", self.arango_no_auth)
        self.with_env(
            "ARANGO_ROOT_PASSWORD", self.arango_root_password)
        self.with_env(
            "ARANGO_RANDOM_ROOT_PASSWORD", self.arango_random_root_password)

    def get_connection_url(self):
        # for now, single host over HTTP
        scheme = 'http'
        port = self.get_exposed_port(self.port_to_expose)
        url = f"{scheme}://{self.get_container_host_ip()}:{port}"

        return url

    def _connect(self):
        wait_for_logs(
            self,
            predicate="is ready for business",
            timeout=MAX_TRIES)
