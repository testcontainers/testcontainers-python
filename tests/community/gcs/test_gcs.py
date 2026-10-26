import os

from testcontainers.community.gcs import GcsContainer


def test_gcs_upload_and_download():
    with GcsContainer() as gcs:
        client = gcs.get_client()
        bucket = client.create_bucket("test-bucket")
        bucket.blob("hello.txt").upload_from_string("Hello, GCS!")

        assert bucket.blob("hello.txt").download_as_text() == "Hello, GCS!"
        assert [blob.name for blob in client.list_blobs("test-bucket")] == ["hello.txt"]


def test_gcs_object_links_use_mapped_port():
    with GcsContainer() as gcs:
        blob = gcs.get_client().create_bucket("test-bucket").blob("hello.txt")
        blob.upload_from_string("Hello, GCS!")
        blob.reload()

        assert blob.media_link.startswith(gcs.get_url())


def test_gcs_resumable_upload():
    # larger than the client's 8 MiB multipart limit, so a resumable upload is used
    data = os.urandom(10 * 1024 * 1024)
    with GcsContainer() as gcs:
        blob = gcs.get_client().create_bucket("test-bucket").blob("big.bin")
        blob.upload_from_string(data)

        assert blob.download_as_bytes() == data


def test_gcs_custom_project():
    with GcsContainer(project="my-project") as gcs:
        assert gcs.get_client().project == "my-project"
