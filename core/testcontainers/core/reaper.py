from __future__ import annotations

from socket import socket
from typing import TYPE_CHECKING, Union

from .config import RYUK_DOCKER_SOCKET, RYUK_IMAGE, RYUK_PRIVILEGED
from .labels import LABEL_SESSION_ID, SESSION_ID
from .utils import setup_logger
from .waiting_utils import wait_for_logs

if TYPE_CHECKING:
    from .container import DockerContainer


logger = setup_logger(__name__)


class Reaper:
    _instance: Union[Reaper, None] = None
    _container: "Union[DockerContainer, None]" = None  # noqa: UP037 Use quotes for type annotation due to circular deps
    _socket: Union[socket, None] = None

    @classmethod
    def get_instance(cls) -> Reaper:
        if not Reaper._instance:
            Reaper._instance = Reaper._create_instance()

        return Reaper._instance

    @classmethod
    def delete_instance(cls) -> None:
        if Reaper._socket is not None:
            Reaper._socket.close()
            Reaper._socket = None

        if Reaper._container is not None:
            Reaper._container.stop()
            Reaper._container = None

        if Reaper._instance is not None:
            Reaper._instance = None

    @classmethod
    def _create_instance(cls) -> Reaper:
        from .container import DockerContainer

        logger.debug(f"Creating new Reaper for session: {SESSION_ID}")

        Reaper._container = (
            DockerContainer(RYUK_IMAGE)
            .with_name(f"testcontainers-ryuk-{SESSION_ID}")
            .with_exposed_ports(8080)
            .with_volume_mapping(RYUK_DOCKER_SOCKET, "/var/run/docker.sock", "rw")
            .with_kwargs(privileged=RYUK_PRIVILEGED)
            .start()
        )
        wait_for_logs(Reaper._container, r".* Started!")

        container_host = Reaper._container.get_container_host_ip()
        container_port = int(Reaper._container.get_exposed_port(8080))

        Reaper._socket = socket()
        Reaper._socket.connect((container_host, container_port))
        Reaper._socket.send(f"label={LABEL_SESSION_ID}={SESSION_ID}\r\n".encode())

        Reaper._instance = Reaper()

        return Reaper._instance
