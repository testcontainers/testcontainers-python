import time
from io import BytesIO
from tarfile import TarFile, TarInfo
from typing import TYPE_CHECKING, Optional

import bcrypt
from requests import get
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, ReadTimeout

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready

if TYPE_CHECKING:
    from requests import Response


class DockerRegistryContainer(DockerContainer):
    # https://docs.docker.com/registry/
    credentials_path: str = "/htpasswd/credentials.txt"

    def __init__(
        self,
        image: str = "registry:2",
        port: int = 5000,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.port: int = port
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.with_exposed_ports(self.port)

    def _copy_credentials(self) -> None:
        # Create credentials and write them to the container
        hashed_password: str = bcrypt.hashpw(
            self.password.encode("utf-8"),
            bcrypt.gensalt(rounds=12, prefix=b"2a"),
        ).decode("utf-8")
        content: bytes = f"{self.username}:{hashed_password}".encode("utf-8")  # noqa: UP012

        with BytesIO() as tar_archive_object, TarFile(fileobj=tar_archive_object, mode="w") as tmp_tarfile:
            tarinfo: TarInfo = TarInfo(name=self.credentials_path)
            tarinfo.size = len(content)
            tarinfo.mtime = time.time()

            tmp_tarfile.addfile(tarinfo, BytesIO(content))
            tar_archive_object.seek(0)
            self.get_wrapped_container().put_archive("/", tar_archive_object)

    @wait_container_is_ready(ConnectionError, ReadTimeout)
    def _readiness_probe(self) -> None:
        url: str = f"http://{self.get_registry()}/v2"
        if self.username and self.password:
            response: Response = get(url, auth=HTTPBasicAuth(self.username, self.password), timeout=1)
        else:
            response: Response = get(url, timeout=1)
        response.raise_for_status()

    def start(self):
        if self.username and self.password:
            self.with_env("REGISTRY_AUTH_HTPASSWD_REALM", "local-registry")
            self.with_env("REGISTRY_AUTH_HTPASSWD_PATH", self.credentials_path)
            super().start()
            self._copy_credentials()
        else:
            super().start()

        self._readiness_probe()
        return self

    def get_registry(self) -> str:
        host: str = self.get_container_host_ip()
        port: str = self.get_exposed_port(self.port)
        return f"{host}:{port}"
