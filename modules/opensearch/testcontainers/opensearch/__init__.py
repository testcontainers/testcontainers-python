from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError, TransportError
from urllib3.exceptions import ProtocolError

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready


class OpenSearchContainer(DockerContainer):
    """
    The following example demonstrates how to create a new index in an OpenSearch container and add
    a document to it. It also shows how to search within the created index. The refresh step in
    between makes sure that the newly created document is available for search.

    The method :code:`get_client` can be used to create a OpenSearch Python Client. The method
    :code:`get_config` can be used to retrieve the host, port, username, and password of the
    container.

    Example:

        .. doctest::

            >>> from testcontainers.opensearch import OpenSearchContainer

            >>> with OpenSearchContainer() as opensearch:
            ...   client = opensearch.get_client()
            ...   creation_result = client.index(index="test", body={"test": "test"})
            ...   refresh_result = client.indices.refresh(index="test")
            ...   search_result = client.search(index="test", body={"query": {"match_all": {}}})
    """

    def __init__(
        self,
        image: str = "opensearchproject/opensearch:2.4.0",
        port: int = 9200,
        security_enabled: bool = False,
        **kwargs,
    ) -> None:
        """
        Args:
            image: Docker image to use for the container.
            port: Port to expose on the container.
            security_enabled: :code:`False` disables the security plugin in OpenSearch.
        """
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.security_enabled = security_enabled

        self.with_exposed_ports(self.port)
        self.with_env("discovery.type", "single-node")
        self.with_env("plugins.security.disabled", "false" if security_enabled else "true")
        if security_enabled:
            self.with_env("plugins.security.allow_default_init_securityindex", "true")

    def get_config(self) -> dict:
        """This method returns the configuration of the OpenSearch container,
        including the host, port, username, and password.

        Returns:
            dict: {`host`: str, `port`: str, `username`: str, `password`: str}
        """

        return {
            "host": self.get_container_host_ip(),
            "port": self.get_exposed_port(self.port),
            "username": "admin",
            "password": "admin",
        }

    def get_client(self, verify_certs: bool = False, **kwargs) -> OpenSearch:
        """Returns a OpenSearch client to connect to the container.

        Returns:
            OpenSearch: Python OpenSearch Client according to
                   https://opensearch.org/docs/latest/clients/python/
        """
        config = self.get_config()
        return OpenSearch(
            hosts=[
                {
                    "host": config["host"],
                    "port": config["port"],
                }
            ],
            http_auth=(config["username"], config["password"]),
            use_ssl=self.security_enabled,
            verify_certs=verify_certs,
            **kwargs,
        )

    @wait_container_is_ready(ConnectionError, TransportError, ProtocolError, ConnectionResetError)
    def _healthcheck(self) -> None:
        """This is an internal method used to check if the OpenSearch container
        is healthy and ready to receive requests."""
        client: OpenSearchContainer = self.get_client()
        client.cluster.health(wait_for_status="green")

    def start(self) -> "OpenSearchContainer":
        """This method starts the OpenSearch container and runs the healthcheck
        to verify that the container is ready to use."""
        super().start()
        self._healthcheck()
        return self
