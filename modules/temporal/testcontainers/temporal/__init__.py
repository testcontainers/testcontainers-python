import urllib.error
import urllib.parse
import urllib.request

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class TemporalContainer(DockerContainer):
    """Temporal dev server container for integration testing.

    Example:

        The example spins up a Temporal dev server and connects to it using the
        ``temporalio`` Python SDK.

        .. doctest::

            >>> from testcontainers.temporal import TemporalContainer
            >>> with TemporalContainer() as temporal:
            ...     address = temporal.get_grpc_address()
    """

    GRPC_PORT = 7233
    HTTP_PORT = 8233

    def __init__(self, image: str = "temporalio/temporal:1.5.1", **kwargs) -> None:
        super().__init__(image, **kwargs)
        self.with_exposed_ports(self.GRPC_PORT, self.HTTP_PORT)
        self.with_command("server start-dev --ip 0.0.0.0")

    @wait_container_is_ready(urllib.error.URLError, ConnectionError)
    def _healthcheck(self) -> None:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.HTTP_PORT)
        url = urllib.parse.urlunsplit(("http", f"{host}:{port}", "/api/v1/namespaces", "", ""))
        urllib.request.urlopen(url, timeout=1)

    def start(self) -> "TemporalContainer":
        super().start()
        self._healthcheck()
        return self

    def get_grpc_address(self) -> str:
        """Returns ``host:port`` for the Temporal gRPC frontend.

        The address intentionally omits a scheme because the Temporal SDKs
        expect a plain ``host:port`` string.
        """
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.GRPC_PORT)}"

    def get_web_ui_url(self) -> str:
        """Returns the base URL for the Temporal Web UI / HTTP API."""
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.HTTP_PORT)}"
