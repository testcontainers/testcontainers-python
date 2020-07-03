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

    Example
    -------
    ::
        localstack = LocalStackContainer(image="localstack/localstack:0.11.3")
        localstack.with_services("dynamodb", "lambda")
        localstack.start()
        dynamo_endpoint = localstack.get_service_endpoint()
        dynamo_client = boto3.client("dynamodb", endpoint_url=dynamo_endpoint)
        scan_result = dynamo_client.scan(TableName='foo')
        # Do something with the scan result
    """
    EDGE_PORT = 4566
    IMAGE = 'localstack/localstack:0.11.3'

    def __init__(self, image=IMAGE):
        super(LocalStackContainer, self).__init__(image)
        self.with_exposed_ports(LocalStackContainer.EDGE_PORT)
        self.with_volume_mapping('/var/run/docker.sock', '/var/run/docker.sock')

    def with_services(self, *services):
        """
        Restrict what services to run.
        If you don't call this, everything will be launched by default.
        """
        self.with_env('SERVICES', ','.join(services))

    def get_endpoint_override(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(LocalStackContainer.EDGE_PORT)
        return f'http://{host}:{port}'

    def start(self):
        super().start()
        self._get_ready_log()
        return self

    def _get_ready_log(self, timeout=30):
        wait_for_logs(self, 'Ready\\.', timeout=timeout)
