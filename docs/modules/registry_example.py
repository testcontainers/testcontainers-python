import json

import requests

from testcontainers.registry import RegistryContainer


def basic_example():
    with RegistryContainer() as registry:
        # Get connection parameters
        host = registry.get_container_host_ip()
        port = registry.get_exposed_port(registry.port)
        registry_url = f"http://{host}:{port}"
        print(f"Registry URL: {registry_url}")

        # Get registry version
        version_response = requests.get(f"{registry_url}/v2/")
        print(f"Registry version: {version_response.headers.get('Docker-Distribution-Api-Version')}")

        # List repositories
        catalog_response = requests.get(f"{registry_url}/v2/_catalog")
        repositories = catalog_response.json()["repositories"]
        print("\nRepositories:")
        print(json.dumps(repositories, indent=2))

        # Create test repository
        test_repo = "test-repo"
        test_tag = "latest"

        # Create a simple manifest
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "config": {
                "mediaType": "application/vnd.docker.container.image.v1+json",
                "size": 1000,
                "digest": "sha256:1234567890abcdef",
            },
            "layers": [
                {
                    "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                    "size": 2000,
                    "digest": "sha256:abcdef1234567890",
                }
            ],
        }

        # Upload manifest
        manifest_url = f"{registry_url}/v2/{test_repo}/manifests/{test_tag}"
        headers = {"Content-Type": "application/vnd.docker.distribution.manifest.v2+json"}
        manifest_response = requests.put(manifest_url, json=manifest, headers=headers)
        print(f"\nUploaded manifest: {manifest_response.status_code}")

        # List tags for repository
        tags_url = f"{registry_url}/v2/{test_repo}/tags/list"
        tags_response = requests.get(tags_url)
        tags = tags_response.json()["tags"]
        print("\nTags:")
        print(json.dumps(tags, indent=2))

        # Get manifest
        manifest_response = requests.get(manifest_url, headers=headers)
        manifest_data = manifest_response.json()
        print("\nManifest:")
        print(json.dumps(manifest_data, indent=2))

        # Get manifest digest
        digest = manifest_response.headers.get("Docker-Content-Digest")
        print(f"\nManifest digest: {digest}")

        # Delete manifest
        delete_response = requests.delete(manifest_url)
        print(f"\nDeleted manifest: {delete_response.status_code}")

        # Verify deletion
        verify_response = requests.get(manifest_url)
        print(f"Manifest exists: {verify_response.status_code == 200}")

        # Get registry configuration
        config_url = f"{registry_url}/v2/"
        config_response = requests.get(config_url)
        print("\nRegistry configuration:")
        print(json.dumps(dict(config_response.headers), indent=2))

        # Get registry health
        health_url = f"{registry_url}/v2/"
        health_response = requests.get(health_url)
        print(f"\nRegistry health: {health_response.status_code == 200}")


if __name__ == "__main__":
    basic_example()
