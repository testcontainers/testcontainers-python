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

from os import PathLike
from typing import Any, Optional, TypedDict, Union

from docker.types.containers import DeviceRequest
from requests import get

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class OllamaModel(TypedDict):
    name: str
    model: str
    modified_at: str
    size: int
    digest: str
    details: dict[str, Any]


class OllamaContainer(DockerContainer):
    """
    Ollama Container

    Example:

        .. doctest::

            >>> from testcontainers.ollama import OllamaContainer
            >>> with OllamaContainer() as ollama:
            ...     ollama.list_models()
            []
    """

    OLLAMA_PORT = 11434

    def __init__(
        self,
        image: str = "ollama/ollama:0.1.44",
        ollama_dir: Optional[Union[str, PathLike]] = None,
        **kwargs,
        #
    ):
        super().__init__(image=image, **kwargs)
        self.ollama_dir = ollama_dir
        self.with_exposed_ports(OllamaContainer.OLLAMA_PORT)
        self._check_and_add_gpu_capabilities()

    def _check_and_add_gpu_capabilities(self):
        info = self.get_docker_client().client.info()
        if "nvidia" in info["Runtimes"]:
            self._kwargs = {**self._kwargs, "device_requests": DeviceRequest(count=-1, capabilities=[["gpu"]])}

    def start(self) -> "OllamaContainer":
        """
        Start the Ollama server
        """
        if self.ollama_dir:
            self.with_volume_mapping(self.ollama_dir, "/root/.ollama", "rw")
        super().start()
        wait_for_logs(self, "Listening on ", timeout=30)

        return self

    def get_endpoint(self):
        """
        Return the endpoint of the Ollama server
        """
        host = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(OllamaContainer.OLLAMA_PORT)
        url = f"http://{host}:{exposed_port}"
        return url

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

    def list_models(self) -> list[OllamaModel]:
        endpoint = self.get_endpoint()
        response = get(url=f"{endpoint}/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])

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
                repository=image_name, conf={"Labels": {"org.testcontainers.session-id": ""}}
            )
