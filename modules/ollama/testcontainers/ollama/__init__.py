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

import docker
from docker.types.containers import DeviceRequest

from testcontainers.core.generic import ServerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class OllamaContainer(ServerContainer):
    def __init__(self, image="ollama/ollama:latest"):
        self.port = 11434
        super().__init__(port=self.port, image=image)
        self.with_exposed_ports(self.port)
        self._check_and_add_gpu_capabilities()

    def _check_and_add_gpu_capabilities(self):
        info = docker.APIClient().info()
        if "nvidia" in info["Runtimes"]:
            self.with_kwargs(device_requests=DeviceRequest(count=-1, capabilities=[["gpu"]]))

    def start(self) -> "OllamaContainer":
        """
        Start the Ollama server
        """
        super().start()
        wait_container_is_ready(self, "Ollama started successfully")
        self._connect()

        return self

    def get_endpoint(self):
        """
        Return the endpoint of the Ollama server
        """
        return self._create_connection_url()

    @property
    def id(self) -> str:
        """
        Return the container object
        """
        return self._container.id

    def pull_model(self, model_name: str) -> None:
        """
        Pull a model from the Ollama server

        Args:
            model_name (str): Name of the model
        """
        self.exec(f"ollama pull {model_name}")

    def commit_to_image(self, image_name: str) -> None:
        """
        Commit the current container to a new image

        Args:
            image_name (str): Name of the new image
        """
        docker_client = self.get_docker_client()
        existing_images = docker_client.client.images.list(name=image_name)
        if not existing_images and self.id:
            docker_client.client.containers.get(self.id).commit(
                repository=image_name,
                tag=image_name.split(":")[-1] if ":" in image_name else "latest",
                conf={"Labels": {"org.testcontainers.session-id": ""}},
            )
