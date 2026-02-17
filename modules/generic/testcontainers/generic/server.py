from typing import Union

import httpx

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.image import DockerImage
from testcontainers.core.wait_strategies import HttpWaitStrategy

# This comment can be removed (Used for testing)


class ServerContainer(DockerContainer):
    """
    Container for a generic server that is based on a custom image.

    Example:

    .. doctest::

        >>> import httpx
        >>> from testcontainers.generic import ServerContainer
        >>> from testcontainers.core.waiting_utils import wait_for_logs
        >>> from testcontainers.core.image import DockerImage

        >>> with DockerImage(path="./modules/generic/tests/samples/python_server", tag="test-srv:latest") as image:
        ...     with ServerContainer(port=9000, image=image) as srv:
        ...         url = srv._create_connection_url()
        ...         response = httpx.get(f"{url}", timeout=5)
        ...         assert response.status_code == 200, "Response status code is not 200"
        ...         delay = wait_for_logs(srv, "GET / HTTP/1.1")


    :param port: Port to be exposed on the container.
    :param image: Docker image to be used for the container.
    """

    def __init__(self, port: int, image: Union[str, DockerImage]) -> None:
        super().__init__(str(image))
        self.internal_port = port
        self.with_exposed_ports(self.internal_port)

    def _connect(self) -> None:
        strategy = HttpWaitStrategy(self.internal_port).for_status_code(404)
        strategy.wait_until_ready(self)

    def get_api_url(self) -> str:
        raise NotImplementedError

    def _create_connection_url(self) -> str:
        if self._container is None:
            raise ContainerStartException("container has not been started")
        host = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.internal_port)
        url = f"http://{host}:{exposed_port}"
        return url

    def start(self) -> "ServerContainer":
        super().start()
        self._connect()
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        super().stop(force, delete_volume)

    def get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self.get_api_url())

    def get_stdout(self) -> str:
        return self.get_logs()[0].decode("utf-8")
