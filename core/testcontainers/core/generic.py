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
from pathlib import Path
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.exceptions import ContainerStartException
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
        url = f"{dialect}://{username}:{password}@{host}:{port}"
        if dbname:
            url = f"{url}/{dbname}"
        return url

    def start(self) -> "DbContainer":
        self._configure()
        super().start()
        self._connect()
        self._seed()
        return self

    def _configure(self) -> None:
        raise NotImplementedError

    def _seed(self) -> None:
        raise NotImplementedError

    def _setup_seed(self, seed):
        self.seed_scripts = None
        self.seed_mount = "/seeds"  # TODO: Should it be configurable?
        if seed is not None:
            seed_localpath, seed_scripts = seed
            seed_abspath = Path(seed_localpath).absolute()
            self.with_volume_mapping(seed_abspath, self.seed_mount)
            self.seed_scripts = seed_scripts
