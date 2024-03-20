from azure.storage.blob import BlobServiceClient

from testcontainers.azurite import AzuriteContainer


def test_docker_run_azurite():
    with AzuriteContainer() as azurite_container:
        blob_service_client = BlobServiceClient.from_connection_string(
            azurite_container.get_connection_string(), api_version="2019-12-12"
        )

        blob_service_client.create_container("test-container")
