from azure.storage.blob import BlobClient, BlobServiceClient
import os


def hello_from_external_container():
    """
    Entry point function for a custom Docker container to test connectivity
    and operations with Azurite (or Azure Blob Storage).

    This function is designed to run inside a separate container within the
    same Docker network as an Azurite instance. It retrieves connection
    details from environment variables and attempts to create a new
    blob container on the connected storage account.
    """
    connection_string = os.environ["AZURE_CONNECTION_STRING"]
    container_to_create = os.environ["AZURE_CONTAINER"]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # create dummy container just to make sure we can process the
    try:
        blob_service_client.create_container(name=container_to_create)
        print("Azure Storage Container created.")
    except Exception as e:
        print(f"Something went wrong : {e}")


if __name__ == "__main__":
    hello_from_external_container()
