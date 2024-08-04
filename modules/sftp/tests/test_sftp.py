import tempfile
from pathlib import Path

import paramiko
import pytest

from testcontainers.sftp import SFTPContainer, SFTPUser


def test_sftp_login_with_default_basic_auth():
    with SFTPContainer() as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=sftp_container.users[0].name,
            password=sftp_container.users[0].password,
        )


def test_sftp_login_with_default_keypair_auth():
    with SFTPContainer() as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=sftp_container.users[1].name,
            key_filename=sftp_container.users[1].private_key_file,
        )


def test_sftp_login_with_custom_user_basic_auth():
    user = SFTPUser(name="custom", password="custom_password")
    with SFTPContainer(users=[user]) as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=user.name,
            password=user.password,
        )


def test_sftp_login_with_custom_user_keypair_auth():
    user = SFTPUser.with_keypair(name="custom")
    with SFTPContainer(users=[user]) as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=user.name,
            key_filename=user.private_key_file,
        )


def test_sftp_login_with_custom_user_password_and_keypair_auth():
    user = SFTPUser.with_keypair(name="custom", password="custom_password")
    with SFTPContainer(users=[user]) as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=user.name,
            password=user.password,
            key_filename=user.private_key_file,
        )


def test_sftp_user_can_upload():
    with SFTPContainer() as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=sftp_container.users[0].name,
            password=sftp_container.users[0].password,
        )
        sftp = ssh.open_sftp()
        sftp.chdir("upload")
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"test")
            f.seek(0)
            sftp.put(f.name, "test.txt")

        with tempfile.NamedTemporaryFile() as f:
            sftp.get("test.txt", f.name)
            f.seek(0)
            assert f.read() == b"test"


def test_sftp_user_can_download_from_mounted(tmp_path: Path):
    temp_dir = tmp_path / "sub"
    temp_dir.mkdir()
    temp_file = temp_dir / "test.txt"
    temp_file.write_text("test")
    user = SFTPUser.with_keypair(name="custom", mount_dir=temp_dir.as_posix())
    with SFTPContainer(users=[user]) as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=user.name,
            key_filename=user.private_key_file,
        )
        sftp = ssh.open_sftp()
        with tempfile.NamedTemporaryFile() as f:
            sftp.get(temp_file.name, f.name)
            f.seek(0)
            assert f.read() == b"test"


def test_sftp_user_cant_upload_to_root(tmp_path: Path):
    temp_dir = tmp_path / "sub"
    temp_dir.mkdir()
    temp_file = temp_dir / "test.txt"
    temp_file.write_text("test")
    with SFTPContainer() as sftp_container:
        sftp_container.start()
        host_ip = sftp_container.get_container_host_ip()
        host_port = sftp_container.get_exposed_sftp_port()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host_ip,
            port=host_port,
            username=sftp_container.users[0].name,
            password=sftp_container.users[0].password,
        )
        sftp = ssh.open_sftp()
        with pytest.raises(PermissionError):
            sftp.put(temp_file.as_posix(), temp_file.name)
