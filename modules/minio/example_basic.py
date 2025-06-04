import io
import json
from datetime import timedelta

from minio import Minio

from testcontainers.minio import MinioContainer


def basic_example():
    with MinioContainer() as minio:
        # Get connection parameters
        host = minio.get_container_host_ip()
        port = minio.get_exposed_port(minio.port)
        access_key = minio.access_key
        secret_key = minio.secret_key

        # Create MinIO client
        client = Minio(f"{host}:{port}", access_key=access_key, secret_key=secret_key, secure=False)
        print("Connected to MinIO")

        # Create bucket
        bucket_name = "test-bucket"
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

        # List buckets
        buckets = client.list_buckets()
        print("\nBuckets:")
        for bucket in buckets:
            print(f"- {bucket.name} (created: {bucket.creation_date})")

        # Upload test files
        test_files = {"test1.txt": "Hello from test1", "test2.txt": "Hello from test2", "test3.txt": "Hello from test3"}

        for filename, content in test_files.items():
            data = io.BytesIO(content.encode())
            client.put_object(bucket_name, filename, data, len(content.encode()), content_type="text/plain")
            print(f"Uploaded {filename}")

        # List objects
        objects = client.list_objects(bucket_name)
        print("\nObjects in bucket:")
        for obj in objects:
            print(f"- {obj.object_name} (size: {obj.size} bytes)")

        # Get object
        print("\nObject contents:")
        for filename in test_files:
            response = client.get_object(bucket_name, filename)
            content = response.read().decode()
            print(f"{filename}: {content}")

        # Create directory structure
        client.put_object(
            bucket_name, "folder1/test4.txt", io.BytesIO(b"Hello from test4"), 15, content_type="text/plain"
        )
        print("\nCreated directory structure")

        # List objects with prefix
        objects = client.list_objects(bucket_name, prefix="folder1/")
        print("\nObjects in folder1:")
        for obj in objects:
            print(f"- {obj.object_name}")

        # Copy object
        client.copy_object(bucket_name, "test1.txt", f"{bucket_name}/folder1/test1_copy.txt")
        print("\nCopied object")

        # Get object metadata
        stat = client.stat_object(bucket_name, "test1.txt")
        print("\nObject metadata:")
        print(
            json.dumps(
                {
                    "name": stat.object_name,
                    "size": stat.size,
                    "content_type": stat.content_type,
                    "last_modified": stat.last_modified.isoformat(),
                },
                indent=2,
            )
        )

        # Generate presigned URL
        url = client.presigned_get_object(bucket_name, "test1.txt", expires=timedelta(hours=1))
        print(f"\nPresigned URL: {url}")

        # Set bucket policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                }
            ],
        }
        client.set_bucket_policy(bucket_name, json.dumps(policy))
        print("\nSet bucket policy")

        # Get bucket policy
        policy = client.get_bucket_policy(bucket_name)
        print("\nBucket policy:")
        print(json.dumps(json.loads(policy), indent=2))

        # Remove objects
        for filename in test_files:
            client.remove_object(bucket_name, filename)
            print(f"Removed {filename}")

        # Remove bucket
        client.remove_bucket(bucket_name)
        print(f"\nRemoved bucket: {bucket_name}")


if __name__ == "__main__":
    basic_example()
