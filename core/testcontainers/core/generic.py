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
import tarfile
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.parse import quote

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

SENTINEL_FOLDER = "/sentinel"
SENTINEL_FILENAME = "completed"
SENTINEL_FULLPATH = f"{SENTINEL_FOLDER}/{SENTINEL_FILENAME}"


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
        if self.seed is None:
            return
        src_path = Path(self.seed)
        container = self.get_wrapped_container()
        transfer_folder(container, src_path, self.seed_mountpoint)
        transfer_file_contents(container, "Sentinel completed", SENTINEL_FOLDER)

    def override_command_for_seed(self, startup_command):
        """Replace the image's command for seed purposes"""
        image_cmd = get_image_cmd(self._docker.client, self.image)
        cmd_full = " ".join([startup_command, image_cmd])
        command = f"""sh -c "
        mkdir {SENTINEL_FOLDER};
        while [ ! -f {SENTINEL_FULLPATH} ];
        do
            sleep 0.1;
        done;
        bash -c '{cmd_full}'"
        """
        self.with_command(command)


def get_image_cmd(client, image):
    image_info = client.api.inspect_image(image)
    cmd_list: list[str] = image_info["Config"]["Cmd"]
    return " ".join(cmd_list)


def transfer_folder(container, local_path, remote_path):
    """Transfer local_path to remote_path on the given container, using put_archive"""
    with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
        for filename in local_path.iterdir():
            tar.add(filename.absolute(), arcname=filename.relative_to(local_path))
        archive.seek(0)
        container.put_archive(remote_path, archive)


def transfer_file_contents(container, content_str, remote_path):
    """Create a file from raw content_str to remote_path on container, via put_archive"""
    with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name=SENTINEL_FILENAME)
        content = BytesIO(bytes(content_str, encoding="utf-8"))
        tarinfo.size = len(content.getvalue())
        tar.addfile(tarinfo, fileobj=content)
        archive.seek(0)
        container.put_archive(remote_path, archive)
