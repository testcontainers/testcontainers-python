from typing import TYPE_CHECKING

from requests import ConnectionError, get

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready

if TYPE_CHECKING:
    from requests import Response


class ChromaContainer(DockerContainer):
    """
    The example below spins up a ChromaDB container, performs a healthcheck and creates a collection.
    The method :code:`get_client` can be used to create a client for the Chroma Python Client.

    Example:

        .. doctest::

            >>> import chromadb
            >>> from testcontainers.chroma import ChromaContainer

            >>> with ChromaContainer() as chroma:
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
        # self.with_command(f"server /data --address :{self.port}")

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

    @wait_container_is_ready(ConnectionError)
    def _healthcheck(self) -> None:
        """This is an internal method used to check if the Chroma container
        is healthy and ready to receive requests."""
        url = f"http://{self.get_config()['endpoint']}/api/v1/heartbeat"
        response: Response = get(url)
        response.raise_for_status()

    def start(self) -> "ChromaContainer":
        """This method starts the Chroma container and runs the healthcheck
        to verify that the container is ready to use."""
        super().start()
        self._healthcheck()
        return self
