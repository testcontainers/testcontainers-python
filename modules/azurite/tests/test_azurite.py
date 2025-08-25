import logging
import time
from pathlib import Path

from azure.storage.blob import BlobServiceClient

from testcontainers.azurite import AzuriteContainer, ConnectionStringType

from testcontainers.core.image import DockerImage
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs


logger = logging.getLogger(__name__)


DOCKER_FILE_PATH = ".modules/azurite/tests/external_container_sample"
IMAGE_TAG = "external_container:test"

TEST_DIR = Path(__file__).parent


def test_docker_run_azurite():
    with AzuriteContainer() as azurite_container:
        blob_service_client = BlobServiceClient.from_connection_string(
            azurite_container.get_connection_string(), api_version="2019-12-12"
        )

        blob_service_client.create_container("test-container")


def test_docker_run_azurite_inter_container_communication():
    """Tests inter-container communication between an Azurite container and a custom
    application container within the same Docker network, while also verifying
    local machine access to Azurite.

    This test case validates the following:
    1.  An Azurite container can be successfully started and configured with a
        custom Docker network and a network alias.
    2.  A custom application container can connect to the Azurite container
        using a network-specific connection string (via its network alias)
        within the shared Docker network.
    3.  The Azurite container remains accessible from the local test machine
        using a host-specific connection string.
    4.  Operations performed by the custom container on Azurite (e.g., creating
        a storage container) are visible and verifiable from the local machine.
    """
    container_name = "test-container"
    with Network() as network:
        with (
            AzuriteContainer()
            .with_network(network)
            .with_network_aliases("azurite_server")
            .with_exposed_ports(10000, 10000)
            .with_exposed_ports(10001, 10001) as azurite_container
        ):
            network_connection_string = azurite_container.get_connection_string(ConnectionStringType.NETWORK)
            local_connection_string = azurite_container.get_connection_string()
            with DockerImage(path=TEST_DIR / "samples/network_container", tag=IMAGE_TAG) as image:
                with (
                    DockerContainer(image=str(image))
                    .with_env("AZURE_CONNECTION_STRING", network_connection_string)
                    .with_env("AZURE_CONTAINER", container_name)
                    .with_network(network)
                    .with_network_aliases("network_container")
                    .with_exposed_ports(80, 80) as container
                ):
                    wait_for_logs(container, "Azure Storage Container created.")
                blob_service_client = BlobServiceClient.from_connection_string(
                    local_connection_string, api_version="2019-12-12"
                )
                # make sure the container was actually created
                assert container_name in [
                    blob_container["name"] for blob_container in blob_service_client.list_containers()
                ]
