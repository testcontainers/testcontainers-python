"""
ArangoDB container support.
"""
from os import environ
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
    def __init__(self, image="arangodb:latest", port_to_expose=8529, **kwargs):
        super().__init__(image=image)
        self.port_to_expose = 8529
        self.with_exposed_ports(self.port_to_expose)

        self.arango_host = kwargs.get('ARANGO_HOST', 'localhost')

        # https://www.arangodb.com/docs/stable/deployment-single-instance-manual-start.html
        self.arango_no_auth = kwargs.get(
            'ARANGO_NO_AUTH', environ.get('ARANGO_NO_AUTH'))
        self.arango_root_password = kwargs.get(
            'ARANGO_ROOT_PASSWORD', environ.get('ARANGO_ROOT_PASSWORD', 'passwd'))
        self.arango_random_root_password = kwargs.get(
            'ARANGO_RANDOM_ROOT_PASSWORD', environ.get('ARANGO_RANDOM_ROOT_PASSWORD'))

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
        url = f"{scheme}://{self.arango_host}:{port}"

        return url

    def _connect(self):
        wait_for_logs(
            self,
            predicate="is ready for business",
            timeout=10)
