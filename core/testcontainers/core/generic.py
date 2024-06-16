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
from typing import Optional, Union
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
from testcontainers.core.image import DockerImage
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError

    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    pass


class DbContainer(DockerContainer):
    """
    **DEPRECATED (for removal)**

    Generic database container.
    """

    @wait_container_is_ready(*ADDITIONAL_TRANSIENT_ERRORS)
    def _connect(self) -> None:
        import sqlalchemy

        engine = sqlalchemy.create_engine(self.get_connection_url())
        try:
            engine.connect()
        finally:
            engine.dispose()

    def get_connection_url(self) -> str:
        raise NotImplementedError

    def _create_connection_url(
        self,
        dialect: str,
        username: str,
        password: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        dbname: Optional[str] = None,
        **kwargs,
    ) -> str:
        if raise_for_deprecated_parameter(kwargs, "db_name", "dbname"):
            raise ValueError(f"Unexpected arguments: {','.join(kwargs)}")
        if self._container is None:
            raise ContainerStartException("container has not been started")
        host = host or self.get_container_host_ip()
        port = self.get_exposed_port(port)
        quoted_password = quote(password, safe=" +")
        url = f"{dialect}://{username}:{quoted_password}@{host}:{port}"
        if dbname:
            url = f"{url}/{dbname}"
        return url

    def start(self) -> "DbContainer":
        self._configure()
        super().start()
        self._transfer_seed()
        self._connect()
        return self

    def _configure(self) -> None:
        raise NotImplementedError

    def _transfer_seed(self) -> None:
        pass


class ServerContainer(DockerContainer):
    """
    **DEPRECATED - will be moved from core to a module (stay tuned for a final/stable import location)**

    Container for a generic server that is based on a custom image.

    Example:

    .. doctest::

        >>> import httpx
        >>> from testcontainers.core.generic import ServerContainer
        >>> from testcontainers.core.waiting_utils import wait_for_logs
        >>> from testcontainers.core.image import DockerImage

        >>> with DockerImage(path="./core/tests/image_fixtures/python_server", tag="test-srv:latest") as image:
        ...     with ServerContainer(port=9000, image=image) as srv:
        ...         url = srv._create_connection_url()
        ...         response = httpx.get(f"{url}", timeout=5)
        ...         assert response.status_code == 200, "Response status code is not 200"
        ...         delay = wait_for_logs(srv, "GET / HTTP/1.1")


    :param path: Path to the Dockerfile to build the image
    :param tag: Tag for the image to be built (default: None)
    """

    def __init__(self, port: int, image: Union[str, DockerImage]) -> None:
        super().__init__(str(image))
        self.internal_port = port
        self.with_exposed_ports(self.internal_port)

    @wait_container_is_ready(HTTPError)
    def _connect(self) -> None:
        # noinspection HttpUrlsUsage
        url = self._create_connection_url()
        try:
            with urlopen(url) as r:
                assert b"" in r.read()
        except HTTPError as e:
            # 404 is expected, as the server may not have the specific endpoint we are looking for
            if e.code == 404:
                pass
            else:
                raise

    def get_api_url(self) -> str:
        raise NotImplementedError

    def _create_connection_url(self) -> str:
        if self._container is None:
            raise ContainerStartException("container has not been started")
        host = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.internal_port)
        url = f"http://{host}:{exposed_port}"
        return url

    def start(self) -> "ServerContainer":
        super().start()
        self._connect()
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        super().stop(force, delete_volume)
