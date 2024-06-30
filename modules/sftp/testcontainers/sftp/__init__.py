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
from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING, Any, NamedTuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

if TYPE_CHECKING:
    from typing_extensions import Self


class SFTPUser:
    """
    Helper class to define a user for SFTPContainer authentication.

    Constructor args/kwargs:

    * ``name``:        (req.) username
    * ``public_key``:  (opt.) bytes of publickey
    * ``private_key``: (opt.) bytes of privatekey (useful if you want to access \
    them later in test code)
    * ``password``:    (opt.) password
    * ``uid``:         (opt.) user ID
    * ``gid``:         (opt.) group ID
    * ``folders``:     (opt.) folders to create inside the user's directory (e.g. upload/)
    * ``mount_dir``:   (opt.) a local folder to mount to the user's root directory

    Properties:

    * ``public_key_file``:  str path of public key tempfile (gets mounted to \
    SFTPContainer as a volume)
    * ``private_key_file``: str path of private key tempfile (useful to pass to \
    paramiko when connecting to the sftp server using ssh

    Methods:

    * ``with_keypair``: classmethod to create a new user with an auto-generated RSA keypair
    * ``conf``: str configuration string to register user on server


    Example:

        .. doctest::

            >>> from testcontainers.sftp import SFTPUser

            >>> users = [
            ...     SFTPUser("jane", password="secret"),
            ...     SFTPUser.with_keypair("ron", folders=["stuff"]),
            ... ]

            >>> for user in users:
            ...     print(user.name, user.folders[0])
            ...
            jane upload
            ron stuff

            >>> assert users[0].password == "secret"

            >>> assert users[1].public_key is not None

            >>> assert users[1].public_key.decode().startswith("ssh-rsa ")

            >>> assert users[1].private_key is not None

            >>> assert users[1].private_key.decode().startswith("-----BEGIN RSA PRIVATE KEY-----")
    """

    def __init__(
        self,
        name: str,
        *,
        public_key: bytes | None = None,
        private_key: bytes | None = None,
        password: str | None = None,
        uid: str | None = None,
        gid: str | None = None,
        folders: list[str] | None = None,
        mount_dir: str | None = None,
    ) -> None:
        if folders is None:
            folders = ["upload"]
        self.name = name
        self.public_key = public_key
        self.private_key = private_key
        self.password = password
        self.uid = uid
        self.gid = gid
        self.folders = folders
        self.mount_dir = mount_dir

        self.public_key_file: str | None = None
        if self.public_key is not None:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(self.public_key)
                self.public_key_file = f.name

        self.private_key_file: str | None = None
        if self.private_key is not None:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(self.private_key)
                self.private_key_file = f.name

    def __del__(self) -> None:
        """Clean up keypair temp files"""
        if self.public_key_file is not None:
            os.unlink(self.public_key_file)
        if self.private_key_file is not None:
            os.unlink(self.private_key_file)

    @property
    def conf(self) -> str:
        """Configuration string to register user on server"""
        return ":".join(
            [
                self.name,
                self.password or "",
                self.uid or "",
                self.gid or "",
                ",".join(self.folders),
            ]
        )

    @classmethod
    def with_keypair(
        cls,
        name: str,
        password: str | None = None,
        uid: str | None = None,
        gid: str | None = None,
        folders: list[str] | None = None,
        mount_dir: str | None = None,
    ) -> SFTPUser:
        """Construct a new SFTPUser with an auto-generated RSA keypair"""
        keypair = _generate_keypair()
        return SFTPUser(
            name=name,
            public_key=keypair.public_key,
            private_key=keypair.private_key,
            password=password,
            uid=uid,
            gid=gid,
            folders=folders,
            mount_dir=mount_dir,
        )

    def __repr__(self) -> str:
        return (
            f"SFTPUser({self.name}, password={self.password}, uid={self.uid},"
            f" gid={self.gid}, folders={self.folders},"
            f" public_key_file={self.public_key_file},"
            f" private_key_file={self.private_key_file})"
        )


class SFTPContainer(DockerContainer):
    """Test container for an SFTP server.

    Default configuration creates two users, ``basic:password`` and ``keypair``
    which has no password but should use the private key accessible at
    ``my_container.users[1].private_key``.

    **Users can only download from their root user folder, but can upload &
    download from any subfolder** (``upload/`` by default).

    Options:

    * ``users = [SFTPUser("jane", password="secret"), SFTPUser.with_keypair("ron")]`` \
    creates ``jane:secret`` or ``ron`` who uses the private key accessible at \
    ``users[1].private_key``.

    Simple example with basic auth:

        .. doctest::

            >>> import paramiko

            >>> from testcontainers.sftp import SFTPContainer

            >>> with SFTPContainer() as sftp_container:
            ...     host_ip = sftp_container.get_container_host_ip()
            ...     host_port = sftp_container.get_exposed_sftp_port()
            ...     ssh = paramiko.SSHClient()
            ...     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ...     ssh.connect(host_ip, host_port, "basic", "password")
            ...     # ssh.get(...)
            ...     # ssh.listdir()
            ...     # ssh.chdir("upload")
            ...     # ssh.put(...)

    Example with keypair auth:

        .. doctest::

            >>> import paramiko

            >>> from testcontainers.sftp import SFTPContainer

            >>> with SFTPContainer() as sftp_container:
            ...     host_ip = sftp_container.get_container_host_ip()
            ...     host_port = sftp_container.get_exposed_sftp_port()
            ...     ssh = paramiko.SSHClient()
            ...     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ...     private_key_file = sftp_container.users[1].private_key_file
            ...     ssh.connect(host_ip, host_port, "keypair", key_filename=private_key_file)
            ...     # ssh.listdir()
            ...     # ssh.get(...)
            ...     # ssh.chdir("upload")
            ...     # ssh.put(...)
    """

    def __init__(
        self,
        image: str = "atmoz/sftp:alpine",
        port: int = 22,
        *,
        users: list[SFTPUser] | None = None,
        **kwargs: Any,
    ) -> None:
        if users is None:
            users = [
                SFTPUser(name="basic", password="password"),
                SFTPUser.with_keypair(name="keypair"),
            ]

        super().__init__(image=image, **kwargs)
        self.port = port
        self.users = users

    @property
    def _users_conf(self) -> str:
        return " ".join(user.conf for user in self.users)

    def _configure(self) -> None:
        for user in self.users:
            if user.public_key_file is not None:
                self.with_volume_mapping(
                    user.public_key_file,
                    f"/home/{user.name}/.ssh/keys/{user.name}.pub",
                )
            if user.mount_dir is not None:
                self.with_volume_mapping(
                    user.mount_dir,
                    f"/home/{user.name}/",
                    "rw",
                )
        self.with_env("SFTP_USERS", self._users_conf)
        self.with_exposed_ports(self.port)

    def start(self) -> Self:
        super().start()
        wait_for_logs(self, f".*Server listening on 0.0.0.0 port {self.port}.*")
        return self

    def get_exposed_sftp_port(self) -> int:
        return int(self.get_exposed_port(self.port))


class _Keypair(NamedTuple):
    """RSA keypair as bytes"""

    private_key: bytes
    public_key: bytes


def _generate_keypair() -> _Keypair:
    """Generate RSA keypair as bytes in OpenSSH format."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,  # paramiko flakiness fix
        format=serialization.PublicFormat.OpenSSH,
    )
    return _Keypair(
        private_key=private_key_bytes,
        public_key=public_key_bytes,
    )
