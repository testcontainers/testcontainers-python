import io

from testcontainers.minio import MinioContainer


def test_docker_run_minio():
    config = MinioContainer(access_key="test-access", secret_key="test-secret")
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
