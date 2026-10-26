#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import json
from typing import TYPE_CHECKING
from urllib.request import Request, urlopen

from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

if TYPE_CHECKING:
    from google.cloud import storage

__all__ = ["GcsContainer"]


class GcsContainer(DockerContainer):
    """
    Google Cloud Storage emulator container based on `fake-gcs-server <https://github.com/fsouza/fake-gcs-server>`_.

    Example:

        .. doctest::

            >>> from testcontainers.community.gcs import GcsContainer

            >>> with GcsContainer() as gcs:
            ...    client = gcs.get_client()
            ...    bucket = client.create_bucket("my-bucket")
            ...    bucket.blob("hello.txt").upload_from_string("Hello, GCS!")
            ...    content = bucket.blob("hello.txt").download_as_text()
            >>> content
            'Hello, GCS!'
    """

    def __init__(
        self,
        image: str = "fsouza/fake-gcs-server:1.56.1",
        port: int = 4443,
        project: str = "test-project",
        **kwargs: object,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.port = port
        self.project = project
        self.with_exposed_ports(self.port)
        self.with_command(f"-scheme http -port {self.port} -backend memory")
        self.waiting_for(HttpWaitStrategy(self.port, "/storage/v1/b"))

    def get_url(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"

    def start(self) -> Self:
        super().start()
        self._update_external_url()
        return self

    def _update_external_url(self) -> None:
        # fake-gcs-server builds object links (e.g. mediaLink) from its external URL,
        # and the host-mapped port is only known once the container is running.
        request = Request(
            f"{self.get_url()}/_internal/config",
            data=json.dumps({"externalUrl": self.get_url()}).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urlopen(request, timeout=10):
            pass

    def get_client(self, **kwargs: object) -> "storage.Client":
        """Get a ``google.cloud.storage.Client`` connected to the emulator.

        Requires the ``google-cloud-storage`` package to be installed.
        """
        from google.auth.credentials import AnonymousCredentials
        from google.cloud import storage

        return storage.Client(
            project=self.project,
            credentials=AnonymousCredentials(),
            client_options={"api_endpoint": self.get_url()},
            **kwargs,
        )
