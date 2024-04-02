from typing_extensions import override

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_for_http


class ChromaContainer(DockerContainer):
    """
    The example below spins up a ChromaDB container, performs a healthcheck and creates a collection.
    The method :code:`get_client` can be used to create a client for the Chroma Python Client.

    Example:

        .. doctest::

            >>> import chromadb
            >>> from testcontainers.chroma import ChromaContainer

            >>> with ChromaContainer("chromadb/chroma:0.4.24") as chroma:
            ...   config = chroma.get_config()
            ...   client = chromadb.HttpClient(host=config["host"], port=config["port"])
            ...   col = client.get_or_create_collection("test")
            ...   col.name
            'test'
    """

    def __init__(
        self,
        image: str = "chromadb/chroma:latest",
        port: int = 8000,
        **kwargs,
    ) -> None:
        """
        Args:
            image: Docker image to use for the MinIO container.
            port: Port to expose on the container.
            access_key: Access key for client connections.
            secret_key: Secret key for client connections.
        """
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port

        self.with_exposed_ports(self.port)

    def get_config(self) -> dict:
        """This method returns the configuration of the Chroma container,
        including the endpoint.

        Returns:
            dict: {`endpoint`: str}
        """
        host_ip = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.port)
        return {
            "endpoint": f"{host_ip}:{exposed_port}",
            "host": host_ip,
            "port": exposed_port,
        }

    @override
    def _wait_until_ready(self) -> None:
        wait_for_http(f"http://{self.get_config()['endpoint']}/api/v1/heartbeat")
