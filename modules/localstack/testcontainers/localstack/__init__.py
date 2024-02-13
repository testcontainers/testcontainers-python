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
import functools as ft
import os
from typing import Any, Optional

import boto3

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class LocalStackContainer(DockerContainer):
    """
    Localstack container.

    Example:

        .. doctest::

            >>> from testcontainers.localstack import LocalStackContainer

            >>> with LocalStackContainer(image="localstack/localstack:2.0.1") as localstack:
            ...     dynamo_client = localstack.get_client("dynamodb")
            ...     tables = dynamo_client.list_tables()
            >>> tables
            {'TableNames': [], ...}
    """

    def __init__(
        self,
        image: str = "localstack/localstack:2.0.1",
        edge_port: int = 4566,
        region_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.edge_port = edge_port
        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION", "us-west-1")
        self.with_exposed_ports(self.edge_port)
        self.with_env("AWS_DEFAULT_REGION", self.region_name)
        self.with_env("AWS_ACCESS_KEY_ID", "testcontainers-localstack")
        self.with_env("AWS_SECRET_ACCESS_KEY", "testcontainers-localstack")

    def with_services(self, *services) -> "LocalStackContainer":
        """
        Restrict what services to run. By default all localstack services are launched.

        Args:
            services: Sequency of services to launch.

        Returns:
            self: Container to allow chaining of 'with_*' calls.
        """
        return self.with_env("SERVICES", ",".join(services))

    def get_url(self) -> str:
        """
        Use this to call localstack instead of real AWS services.
        ex: boto3.client('lambda', endpoint_url=localstack.get_url())
        :return: the endpoint where localstack is reachable.
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.edge_port)
        return f"http://{host}:{port}"

    @ft.wraps(boto3.client)
    def get_client(self, name, **kwargs) -> Any:
        kwargs_ = {
            "endpoint_url": self.get_url(),
            "region_name": self.region_name,
            "aws_access_key_id": "testcontainers-localstack",
            "aws_secret_access_key": "testcontainers-localstack",
        }
        kwargs_.update(kwargs)
        return boto3.client(name, **kwargs_)

    def start(self, timeout: float = 60) -> "LocalStackContainer":
        super().start()
        wait_for_logs(self, r"Ready\.\n", timeout=timeout)
        return self
