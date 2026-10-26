from testcontainers.community.gcs import GcsContainer


def basic_example():
    with GcsContainer() as gcs:
        # Get a client connected to the emulator
        client = gcs.get_client()

        # Create a bucket
        bucket = client.create_bucket("test-bucket")
        print(f"Created bucket: {bucket.name}")

        # Upload objects
        for i in range(1, 4):
            blob = bucket.blob(f"test{i}.txt")
            blob.upload_from_string(f"Hello from object {i}!")
            print(f"Uploaded object: {blob.name}")

        # List objects
        print("\nObjects in bucket:")
        for blob in client.list_blobs(bucket.name):
            print(f"Name: {blob.name}, Size: {blob.size} bytes")

        # Download an object
        content = bucket.blob("test1.txt").download_as_text()
        print(f"\nContent of test1.txt: {content}")


if __name__ == "__main__":
    basic_example()
