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
from unittest.mock import patch

from google.cloud import datastore
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class DatastoreContainer(DockerContainer):
    """
    Datastore container for testing managed message queues.

    Example:

        The example will spin up a Google Cloud Datastore emulator that you can use for integration
        tests. The :code:`datastore` instance provides convenience methods :code:`get_datastore_client` to
        connect to the emulator without having to set the environment variable :code:`DATASTORE_EMULATOR_HOST`.

        .. doctest::

            >>> from testcontainers.google import DatastoreContainer

            >>> config = DatastoreContainer()
            >>> with config as datastore:
            ...    datastore_client = datastore.get_datastore_client()
    """

    def __init__(
        self,
        image: str = "google/cloud-sdk:emulators",
        project: str = "test-project",
        port: int = 8081,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.project = project
        self.port = port
        self.with_exposed_ports(self.port)
        self.with_command(
            f"gcloud beta emulators datastore start --no-store-on-disk --project={project} --host-port=0.0.0.0:{port}"
        )

    def get_datastore_emulator_host(self) -> str:
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"

    def get_datastore_client(self, **kwargs) -> datastore.Client:
        wait_for_logs(self, "Dev App Server is now running.", timeout=30.0)
        env_vars = {
            "DATASTORE_DATASET": self.project,
            "DATASTORE_EMULATOR_HOST": self.get_datastore_emulator_host(),
            "DATASTORE_EMULATOR_HOST_PATH": f"{self.get_datastore_emulator_host()}/datastore",
            "DATASTORE_HOST": f"http://{self.get_datastore_emulator_host()}",
            "DATASTORE_PROJECT_ID": self.project,
        }
        with patch.dict(os.environ, env_vars):
            return datastore.Client(**kwargs)
