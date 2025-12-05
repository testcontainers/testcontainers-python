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
import os
from typing import Optional
from unittest.mock import patch

from google.cloud import storage
from testcontainers.core.container import DockerContainer


class GoogleCloudStorageContainer(DockerContainer):
    """
    GoogleCloudStorage container for testing managed object storage buckets.

    Example:

        The example will spin up a Google Cloud Storage Fake Server that you can use for integration
        tests. The :code:`storage` instance provides convenience methods :code:`get_storage_client` to interact with
        the fake GCS server without having to set the environment variable :code:`STORAGE_EMULATOR_HOST`.

        .. doctest::

            >>> from testcontainers.google import GoogleCloudStorageContainer

            >>> config = GoogleCloudStorageContainer()
            >>> with config as gcs:
            ...    client = gcs.get_storage_client()
            ...    bucket = client.create_bucket("test-bucket")
            ...    bucket = client.create_bucket("test-bucket")
    """

    def __init__(
        self, image: str = "fsouza/fake-gcs-server",
            location: str = "US-CENTRAL1",
            scheme: str = "http",
            port_http: int = 8000,
            data: Optional[str] = None,
            **kwargs
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.location = location
        self.scheme = scheme
        self.port_http = port_http
        self.data = data
        self.with_exposed_ports(self.port_http)
        command = f"-location {location} -scheme={scheme} -port={port_http}"
        if self.data:
            self.with_volume_mapping(self.data, "/data")
            command += " -data /data"



        self.with_command(command)

    def get_gcs_emulator_host(self) -> str:
        return f"{self.scheme}://{self.get_container_host_ip()}:{self.get_exposed_port(self.port_http)}"

    def _get_client(self, cls: type, **kwargs) -> dict:
        with patch.dict(os.environ, STORAGE_EMULATOR_HOST=self.get_gcs_emulator_host()):
            return cls(**kwargs)

    def get_storage_client(self, **kwargs) -> storage.Client:
        from google.auth import credentials

        kwargs["credentials"] = credentials.AnonymousCredentials()
        return self._get_client(storage.Client, **kwargs)
