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

from google.cloud import bigquery

from testcontainers.core.container import DockerContainer


class BigQueryContainer(DockerContainer):
    """
    BigQUery container for testing bigquery warehouse.

    Example:

        The example will spin up a BigQuery emulator that you can use for integration
        tests. The :code:`bigquery` instance provides convenience method :code:`get_bigquery_client`
        to interact with the fake BigQuery Server.

        .. doctest::

            >>> from testcontainers.google import BigQueryContainer

            >>> config = BigQueryContainer()
            >>> with config as bigquery:
            ...    bq = bigquery.get_bigquery_client()
            ...    datasets = bq.list_datasets("test-project")
    """

    def __init__(
            self, image: str = "ghcr.io/goccy/bigquery-emulator:latest", project: str = "test-project",
            dataset: str = "test-containers", port: int = 9050, **kwargs
    ) -> None:
        super().__init__(image=image, platform="linux/x86_64", **kwargs)
        self.project = project
        self.dataset = dataset
        self.port = port
        self.with_exposed_ports(self.port)
        self.with_command(f"--project {self.project} --dataset {self.dataset} --port {self.port}")

    def get_bigquery_emulator_host(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"

    def _get_client(self, cls: type, **kwargs) -> dict:
        return cls(**kwargs)

    def get_bigquery_client(self, **kwargs) -> bigquery.Client:
        from google.auth import credentials

        kwargs["client_options"] = {"api_endpoint": self.get_bigquery_emulator_host()}
        kwargs["credentials"] = credentials.AnonymousCredentials()
        return self._get_client(bigquery.Client, **kwargs)
