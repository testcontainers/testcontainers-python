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
from typing import Optional

from testcontainers.core.container import DockerContainer

VIDEO_DEFAULT_IMAGE = "selenium/video:ffmpeg-6.1-20240402"


class SeleniumVideoContainer(DockerContainer):
    """
    Selenium video container.
    """

    def __init__(self, image: Optional[str] = None, **kwargs) -> None:
        self.image = image or VIDEO_DEFAULT_IMAGE
        super().__init__(image=self.image, **kwargs)

    def set_video_name(self, video_name: str) -> "DockerContainer":
        self.with_env("FILE_NAME", video_name)
        return self

    def set_videos_host_path(self, host_path: str) -> "DockerContainer":
        self.with_volume_mapping(host_path, "/videos", "rw")
        return self

    def set_selenium_container_host(self, host: str) -> "DockerContainer":
        self.with_env("DISPLAY_CONTAINER_NAME", host)
        return self
