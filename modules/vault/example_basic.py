import json

import hvac

from testcontainers.vault import VaultContainer


def basic_example():
    with VaultContainer() as vault:
        # Get connection parameters
        host = vault.get_container_host_ip()
        port = vault.get_exposed_port(vault.port)
        token = vault.token

        # Create Vault client
        client = hvac.Client(url=f"http://{host}:{port}", token=token)
        print("Connected to Vault")

        # Enable KV secrets engine
        client.sys.enable_secrets_engine(backend_type="kv", path="secret", options={"version": "2"})
        print("Enabled KV secrets engine")

        # Write secrets
        test_secrets = {
            "database": {"username": "admin", "password": "secret123", "host": "localhost"},
            "api": {"key": "api-key-123", "endpoint": "https://api.example.com"},
        }

        for path, secret in test_secrets.items():
            client.secrets.kv.v2.create_or_update_secret(path=path, secret=secret)
            print(f"Created secret at: {path}")

        # Read secrets
        print("\nReading secrets:")
        for path in test_secrets:
            secret = client.secrets.kv.v2.read_secret_version(path=path)
            print(f"\nSecret at {path}:")
            print(json.dumps(secret["data"]["data"], indent=2))

        # Enable and configure AWS secrets engine
        client.sys.enable_secrets_engine(backend_type="aws", path="aws")
        print("\nEnabled AWS secrets engine")

        # Configure AWS credentials
        client.secrets.aws.configure_root(
            access_key="test-access-key", secret_key="test-secret-key", region="us-east-1"
        )
        print("Configured AWS credentials")

        # Create a role
        client.secrets.aws.create_role(
            name="test-role",
            credential_type="iam_user",
            policy_document=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [{"Effect": "Allow", "Action": "s3:ListAllMyBuckets", "Resource": "*"}],
                }
            ),
        )
        print("Created AWS role")

        # Generate AWS credentials
        aws_creds = client.secrets.aws.generate_credentials(name="test-role")
        print("\nGenerated AWS credentials:")
        print(json.dumps(aws_creds["data"], indent=2))

        # List enabled secrets engines
        print("\nEnabled secrets engines:")
        for path, engine in client.sys.list_mounted_secrets_engines()["data"].items():
            print(f"Path: {path}, Type: {engine['type']}")


if __name__ == "__main__":
    basic_example()
