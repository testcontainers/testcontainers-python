import json

from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient

from testcontainers.azurite import AzuriteContainer


def basic_example():
    with AzuriteContainer() as azurite:
        # Get connection string
        connection_string = azurite.get_connection_string()

        # Create BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create QueueServiceClient
        queue_service_client = QueueServiceClient.from_connection_string(connection_string)

        # Create a test container
        container_name = "test-container"
        container_client = blob_service_client.create_container(container_name)
        print(f"Created container: {container_name}")

        # Upload test blobs
        test_data = [
            {"name": "test1", "value": 100, "category": "A"},
            {"name": "test2", "value": 200, "category": "B"},
            {"name": "test3", "value": 300, "category": "A"},
        ]

        for i, data in enumerate(test_data, 1):
            blob_name = f"test{i}.json"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(json.dumps(data), overwrite=True)
            print(f"Uploaded blob: {blob_name}")

        # List blobs
        print("\nBlobs in container:")
        for blob in container_client.list_blobs():
            print(f"Name: {blob.name}, Size: {blob.size} bytes")

        # Download and read a blob
        blob_client = container_client.get_blob_client("test1.json")
        blob_data = blob_client.download_blob()
        content = json.loads(blob_data.readall())
        print("\nBlob content:")
        print(json.dumps(content, indent=2))

        # Create a test queue
        queue_name = "test-queue"
        queue_client = queue_service_client.create_queue(queue_name)
        print(f"\nCreated queue: {queue_name}")

        # Send test messages
        test_messages = ["Hello Azurite!", "This is a test message", "Queue is working!"]

        for msg in test_messages:
            queue_client.send_message(msg)
            print(f"Sent message: {msg}")

        # Receive messages
        print("\nReceived messages:")
        for _ in range(len(test_messages)):
            message = queue_client.receive_message()
            if message:
                print(f"Message: {message.content}")
                queue_client.delete_message(message.id, message.pop_receipt)
                print("Deleted message")


if __name__ == "__main__":
    basic_example()
