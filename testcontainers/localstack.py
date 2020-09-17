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
        localstack = LocalStackContainer(image="localstack/localstack:0.11.4")
        localstack.with_services("dynamodb", "lambda")
        localstack.start()
        dynamo_endpoint = localstack.get_url()
        dynamo_client = boto3.client("dynamodb", endpoint_url=dynamo_endpoint)
        scan_result = dynamo_client.scan(TableName='foo')
        # Do something with the scan result
    """
    EDGE_PORT = 4566
    IMAGE = 'localstack/localstack:0.11.4'

    def __init__(self, image=IMAGE):
        super(LocalStackContainer, self).__init__(image)
        self.with_exposed_ports(LocalStackContainer.EDGE_PORT)

    def with_services(self, *services):
        """
        Restrict what services to run. By default all localstack services are launched.
        :return: the DockerContainer to allow chaining of 'with_*' calls.
        """
        return self.with_env('SERVICES', ','.join(services))

    def get_url(self):
        """
        Use this to call localstack instead of real AWS services.
        ex: boto3.client('lambda', endpoint_url=localstack.get_url())
        :return: the endpoint where localstack is reachable.
        """
        host = self.get_container_host_ip()
        port = self.get_exposed_port(LocalStackContainer.EDGE_PORT)
        return 'http://{}:{}'.format(host, port)

    def start(self, timeout=60):
        super().start()
        wait_for_logs(self, r'Ready\.\n', timeout=timeout)
        return self
