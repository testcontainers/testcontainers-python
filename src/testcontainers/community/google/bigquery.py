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
from google.auth.credentials import AnonymousCredentials
from google.cloud import bigquery

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class BigQueryContainer(DockerContainer):
    """
    BigQuery container for testing against a local BigQuery emulator.

    Wraps `goccy/bigquery-emulator <https://github.com/goccy/bigquery-emulator>`_,
    a GoogleSQL implementation over an embedded SQLite database. It is not BigQuery
    itself, so treat query results as a strong signal rather than a guarantee for
    anything outside standard GoogleSQL (BigQuery-specific services like BigQuery ML,
    row access policies, or external tables are out of scope).

    Example:

        The example will spin up a BigQuery emulator that you can use for integration
        tests. The :code:`bigquery` instance provides a convenience method
        :code:`get_client` to connect to the emulator without needing real GCP
        credentials.

        .. doctest::

            >>> from testcontainers.community.google import BigQueryContainer

            >>> with BigQueryContainer() as bigquery:
            ...    client = bigquery.get_client()
            ...    job = client.query("SELECT 1 AS one")
            ...    list(job.result())
            [Row((1,), {'one': 0})]
    """

    def __init__(
        self,
        image: str = "ghcr.io/goccy/bigquery-emulator:latest",
        project: str = "test-project",
        port: int = 9050,
        grpc_port: int = 9060,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.project = project
        self.port = port
        self.grpc_port = grpc_port
        self.with_exposed_ports(self.port, self.grpc_port)
        self.with_command(f"--project={project} --port={port} --grpc-port={grpc_port}")

    def get_rest_endpoint(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"

    def get_client(self, **kwargs: object) -> bigquery.Client:
        wait_for_logs(self, "REST server listening at", timeout=30.0)
        kwargs.setdefault("project", self.project)
        kwargs.setdefault("credentials", AnonymousCredentials())
        kwargs.setdefault("client_options", {"api_endpoint": self.get_rest_endpoint()})
        return bigquery.Client(**kwargs)
