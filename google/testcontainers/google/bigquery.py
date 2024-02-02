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
from testcontainers.core.container import DockerContainer
from google.cloud.bigquery import Client as BigQueryClient
from google.api_core.client_options import ClientOptions
from google.auth.credentials import AnonymousCredentials


class BigQueryContainer(DockerContainer):
    """
    Docker container to emulate BigQuery, based on https://github.com/testcontainers/testcontainers-java/blob/main/modules/gcloud/src/main/java/org/testcontainers/containers/BigQueryEmulatorContainer.java.
    Uses ghcr.io/goccy/bigquery-emulator image by default.
    Example:

        The example will spin up a Google Cloud BigQuery emulator that you can use for integration
        tests.

        .. doctest::

            >>> from testcontainers.google import BigQueryContainer
            >>> from testcontainers.core.waiting_utils import wait_for_logs
            >>> from google.cloud.bigquery import QueryJobConfig

            >>> with BigQueryContainer() as bigquery:
            ...    wait_for_logs(bigquery, "gRPC server listening", timeout=60)
            ...    client = bigquery.get_client()
            ...    result = client.query("SELECT 1", job_config=QueryJobConfig()).result()
            ...    print(result.total_rows)
    """
    def __init__(self, image: str = "ghcr.io/goccy/bigquery-emulator:latest", project: str = "test-project",
                 http_port: int = 9050, grpc_port: int = 9060, **kwargs) -> None:
        super(BigQueryContainer, self).__init__(image=image, **kwargs)
        self.project = project
        self.http_port = http_port
        self.grpc_port = grpc_port
        self.with_exposed_ports(http_port, grpc_port)
        command = [
            "--project", project,
            "--port", str(http_port),
            "--grpc-port", str(grpc_port),
        ]
        self.with_command(' '.join(command))

    def get_emulator_http_endpoint(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.http_port)}"

    def get_client(self) -> BigQueryClient:
        client_options = ClientOptions(api_endpoint=self.get_emulator_http_endpoint())
        return BigQueryClient(
            project=self.project,
            client_options=client_options,
            credentials=AnonymousCredentials(),
        )

