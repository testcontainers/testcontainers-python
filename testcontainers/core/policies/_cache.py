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

from typing import Dict, Iterable, Optional

from docker import DockerClient
from docker.errors import ImageNotFound
from docker.models.images import Image


class _LocalImagesCache:
    def __init__(self):
        self.images_cache: Dict[str, Image] = {}
        self.docker_client: DockerClient = DockerClient.from_env()
        self.initialized: bool = False

    def __getitem__(self, item) -> Image:
        if not self.initialized:
            self.populate(self.docker_client.images.list())
            self.initialized = True

        return self.images_cache[item]

    def refresh(self, image_name: str) -> Optional[Image]:
        try:
            image = self.docker_client.images.get(image_name)
        except ImageNotFound:
            del self.images_cache[image_name]

            return None

        self.populate((image,))

        return image

    def populate(self, images: Iterable[Image]) -> None:
        for image in images:
            self.images_cache.update({tag: image for tag in image.tags})
