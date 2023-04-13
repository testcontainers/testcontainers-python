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
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.container import DockerContainer


class LocalStackContainer(DockerContainer):
    """
    Localstack container.

    Example:

        .. doctest::

            >>> from testcontainers.localstack import LocalStackContainer

            >>> with LocalStackContainer(image="localstack/localstack:0.11.4") as localstack:
            ...     dynamo_endpoint = localstack.get_url()
            <testcontainers.localstack.LocalStackContainer object at 0x...>

        The endpoint can be used to create a client with the boto3 library:

        .. doctest::

            >>> from testcontainers.localstack import LocalStackContainer

            >>> with LocalStackContainer(image="localstack/localstack:0.11.4") as localstack:
            ...     dynamo_endpoint = localstack.get_url()
            ...     dynamo_client = boto3.client("dynamodb", endpoint_url=dynamo_endpoint)
            ...     scan_result = dynamo_client.scan(TableName='foo')
    """
    def __init__(self, image: str = 'localstack/localstack:0.11.4', edge_port: int = 4566,
                 **kwargs) -> None:
        super(LocalStackContainer, self).__init__(image, **kwargs)
        self.edge_port = edge_port
        self.with_exposed_ports(self.edge_port)

    def with_services(self, *services) -> "LocalStackContainer":
        """
        Restrict what services to run. By default all localstack services are launched.

        Args:
            services: Sequency of services to launch.

        Returns:
            self: Container to allow chaining of 'with_*' calls.
        """
        return self.with_env('SERVICES', ','.join(services))

    def get_url(self) -> str:
        """
        Use this to call localstack instead of real AWS services.
        ex: boto3.client('lambda', endpoint_url=localstack.get_url())
        :return: the endpoint where localstack is reachable.
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.edge_port)
        return f'http://{host}:{port}'

    def start(self, timeout: float = 60) -> "LocalStackContainer":
        super().start()
        wait_for_logs(self, r'Ready\.\n', timeout=timeout)
        return self
