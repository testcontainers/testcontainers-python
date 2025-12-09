import json
import os
from datetime import datetime

import paramiko

from testcontainers.sftp import SftpContainer


def basic_example():
    with SftpContainer() as sftp:
        # Get connection parameters
        host = sftp.get_container_host_ip()
        port = sftp.get_exposed_port(sftp.port)
        username = sftp.username
        password = sftp.password

        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password)
        print("Connected to SFTP server")

        # Create SFTP client
        sftp_client = ssh.open_sftp()

        # Create test directory
        test_dir = "/home/testuser/test_dir"
        sftp_client.mkdir(test_dir)
        print(f"Created directory: {test_dir}")

        # Create and upload test files
        test_files = [
            {"name": "test1.txt", "content": "This is test file 1"},
            {"name": "test2.txt", "content": "This is test file 2"},
            {"name": "test3.txt", "content": "This is test file 3"},
        ]

        for file_info in test_files:
            local_path = f"/tmp/{file_info['name']}"
            remote_path = f"{test_dir}/{file_info['name']}"

            # Create local file
            with open(local_path, "w") as f:
                f.write(file_info["content"])

            # Upload file
            sftp_client.put(local_path, remote_path)
            print(f"Uploaded file: {file_info['name']}")

            # Remove local file
            os.remove(local_path)

        # List directory contents
        print("\nDirectory contents:")
        for entry in sftp_client.listdir_attr(test_dir):
            print(
                json.dumps(
                    {
                        "filename": entry.filename,
                        "size": entry.st_size,
                        "modified": datetime.fromtimestamp(entry.st_mtime).isoformat(),
                    },
                    indent=2,
                )
            )

        # Download and read file
        print("\nReading file contents:")
        for file_info in test_files:
            remote_path = f"{test_dir}/{file_info['name']}"
            local_path = f"/tmp/{file_info['name']}"

            # Download file
            sftp_client.get(remote_path, local_path)

            # Read and print contents
            with open(local_path) as f:
                content = f.read()
            print(f"\n{file_info['name']}:")
            print(content)

            # Remove local file
            os.remove(local_path)

        # Create nested directory
        nested_dir = f"{test_dir}/nested"
        sftp_client.mkdir(nested_dir)
        print(f"\nCreated nested directory: {nested_dir}")

        # Move file to nested directory
        old_path = f"{test_dir}/test1.txt"
        new_path = f"{nested_dir}/test1.txt"
        sftp_client.rename(old_path, new_path)
        print("Moved file to nested directory")

        # List nested directory
        print("\nNested directory contents:")
        for entry in sftp_client.listdir_attr(nested_dir):
            print(
                json.dumps(
                    {
                        "filename": entry.filename,
                        "size": entry.st_size,
                        "modified": datetime.fromtimestamp(entry.st_mtime).isoformat(),
                    },
                    indent=2,
                )
            )

        # Get file attributes
        print("\nFile attributes:")
        for file_info in test_files:
            remote_path = f"{test_dir}/{file_info['name']}"
            try:
                attrs = sftp_client.stat(remote_path)
                print(f"\n{file_info['name']}:")
                print(
                    json.dumps(
                        {
                            "size": attrs.st_size,
                            "permissions": oct(attrs.st_mode)[-3:],
                            "modified": datetime.fromtimestamp(attrs.st_mtime).isoformat(),
                        },
                        indent=2,
                    )
                )
            except FileNotFoundError:
                print(f"File not found: {file_info['name']}")

        # Clean up
        sftp_client.close()
        ssh.close()


if __name__ == "__main__":
    basic_example()
