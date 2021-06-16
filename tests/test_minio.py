from testcontainers.minio import MinioContainer


def test_docker_run_minio():
    config = MinioContainer()

    with config as minio:
        minio_client = minio.get_client()
        found = minio_client.bucket_exists("mybucket")
        assert not found
        minio_client.make_bucket("mybucket")
        found = minio_client.bucket_exists("mybucket")
        assert found
