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
import logging
import re
import urllib
from urllib.error import URLError

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready

_FALLBACK_VERSION = 8
"""This version is used when no version could be detected from the image name."""


def _major_version_from_image_name(image_name: str) -> int:
    """Returns the major version from a container name like 'elasticsearch:8.1.0'
    If the major version could not be determined, it will use the most recent
    one (8 at the time of writing 2022-08-11).
    """
    version_string = image_name.split(":")[-1]
    regex_match = re.compile(r"(\d+)\.\d+\.\d+").match(version_string)
    if not regex_match:
        logging.warning(
            "Could not determine major version from image name '%s'. Will use %s", image_name, _FALLBACK_VERSION
        )
        return _FALLBACK_VERSION
    else:
        return int(regex_match.group(1))


def _environment_by_version(version: int) -> dict[str, str]:
    """Returns environment variables required for each major version to work."""
    if version == 6:
        # This setting is needed to avoid the check for the kernel parameter
        # vm.max_map_count in the BootstrapChecks
        return {"discovery.zen.minimum_master_nodes": "1"}
    elif version == 7:
        return {}
    elif version == 8:
        # Elasticsearch uses https now by default. However, our readiness
        # check uses http, which does not work. Hence we disable security
        # which should not be an issue for our context
        return {"xpack.security.enabled": "false"}
    else:
        raise ValueError(f"Unknown elasticsearch version given: {version}")


class ElasticSearchContainer(DockerContainer):
    """
    ElasticSearch container.

    Example:

        .. doctest::

            >>> import json
            >>> import urllib
            >>> from testcontainers.elasticsearch import ElasticSearchContainer

            >>> with ElasticSearchContainer(f'elasticsearch:8.3.3', mem_limit='3G') as es:
            ...    resp = urllib.request.urlopen(es.get_url())
            ...    json.loads(resp.read().decode())['version']['number']
            '8.3.3'
    """

    def __init__(self, image: str = "elasticsearch", port: int = 9200, **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.with_exposed_ports(self.port)
        self.with_env("transport.host", "127.0.0.1")
        self.with_env("http.host", "0.0.0.0")

        major_version = _major_version_from_image_name(image)
        for key, value in _environment_by_version(major_version).items():
            self.with_env(key, value)

    @wait_container_is_ready(URLError)
    def _connect(self) -> None:
        res = urllib.request.urlopen(self.get_url())
        if res.status != 200:
            raise Exception()

    def get_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"

    def start(self) -> "ElasticSearchContainer":
        super().start()
        self._connect()
        return self
