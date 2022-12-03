import io
import socket
from contextlib import closing

from pytest import fixture

from testcontainers.minio import MinioContainer


@fixture
def port_to_expose():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("localhost", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def test_docker_run_minio(port_to_expose):
    config = MinioContainer(
        port_to_expose=port_to_expose,
        access_key="test-access",
        secret_key="test-secret",
    )
    with config as minio:
        client = minio.get_client()
        client.make_bucket("test")
        test_content = b"Hello World"
        client.put_object(
            "test",
            "testfile.txt",
            io.BytesIO(test_content),
            length=len(test_content),
        )

        assert client.get_object("test", "testfile.txt").data == test_content
        assert minio.get_config()["access_key"] == config.access_key
        assert minio.get_config()["secret_key"] == config.secret_key
