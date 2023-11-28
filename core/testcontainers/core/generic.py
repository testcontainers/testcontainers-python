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

from .container import DockerContainer
from .exceptions import ContainerStartException
from .utils import raise_for_deprecated_parameter
from .waiting_utils import wait_container_is_ready

ADDITIONAL_TRANSIENT_ERRORS = []
try:
    from sqlalchemy.exc import DBAPIError
    ADDITIONAL_TRANSIENT_ERRORS.append(DBAPIError)
except ImportError:
    pass


class DbContainer(DockerContainer):
    """
    Generic database container.
    """
    @wait_container_is_ready(*ADDITIONAL_TRANSIENT_ERRORS)
    def _connect(self) -> None:
        import sqlalchemy
        engine = sqlalchemy.create_engine(self.get_connection_url())
        engine.connect()

    def get_connection_url(self) -> str:
        raise NotImplementedError

    def _create_connection_url(self, dialect: str, username: str, password: str,
                               host: Optional[str] = None, port: Optional[int] = None,
                               dbname: Optional[str] = None, **kwargs) -> str:
        if raise_for_deprecated_parameter(kwargs, "db_name", "dbname"):
            raise ValueError(f"Unexpected arguments: {','.join(kwargs)}")
        if self._container is None:
            raise ContainerStartException("container has not been started")
        host = host or self.get_container_host_ip()
        port = self.get_exposed_port(port)
        url = f"{dialect}://{username}:{password}@{host}:{port}"
        if dbname:
            url = f"{url}/{dbname}"
        return url

    def start(self) -> 'DbContainer':
        self._configure()
        super().start()
        self._connect()
        return self

    def _configure(self) -> None:
        raise NotImplementedError
