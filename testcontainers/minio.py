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


from minio import Minio

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class MinioContainer(DockerContainer):

    def __init__(self, image="minio/minio:latest", port_to_expose=9000,
                 access_key="adminAccessKey", secret_key="adminSecretKey", region="us-east-1", secure=False):
        super(MinioContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.secure = secure

        self.with_env("MINIO_ACCESS_KEY", access_key)
        self.with_env("MINIO_SECRET_KEY", secret_key)
        self.with_env("MINIO_REGION", region)

    @wait_container_is_ready()
    def _connect(self):
        self.get_client()

    def get_client(self) -> 'Minio':
        client = Minio(
            "{}:{}".format(self.get_container_host_ip(), self.get_exposed_port(9000)),
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
            region=self.region
        )
        return client

    def start(self):
        self.with_command("server /data")
        super().start()
        self._connect()
        return self
