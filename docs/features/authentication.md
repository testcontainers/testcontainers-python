# Docker Authentication

Testcontainers-Python supports various methods of authenticating with Docker registries. This is essential when working with private registries or when you need to pull images that require authentication.

## Basic Authentication

The simplest way to authenticate is using Docker's built-in credential store. Testcontainers-Python will automatically use credentials stored by Docker:

```python
from testcontainers.generic import GenericContainer

# Docker will automatically use stored credentials
container = GenericContainer("private.registry.com/myimage:latest")
```

## Environment Variables

You can provide registry credentials using environment variables:

```bash
# Set registry credentials
export DOCKER_USERNAME=myuser
export DOCKER_PASSWORD=mypassword
export DOCKER_REGISTRY=private.registry.com
```

## Configuration File

You can also configure authentication in the `.testcontainers.properties` file:

```properties
registry.username=myuser
registry.password=mypassword
registry.url=private.registry.com
```

## Programmatic Authentication

For more control, you can provide credentials programmatically:

```python
from testcontainers.core.config import TestcontainersConfiguration

# Configure registry credentials
config = TestcontainersConfiguration()
config.registry_username = "myuser"
config.registry_password = "mypassword"
config.registry_url = "private.registry.com"

# Use the configuration
container = GenericContainer("private.registry.com/myimage:latest")
```

## AWS ECR Authentication

For Amazon Elastic Container Registry (ECR), Testcontainers-Python supports automatic authentication:

```python
from testcontainers.generic import GenericContainer

# ECR authentication is handled automatically
container = GenericContainer("123456789012.dkr.ecr.region.amazonaws.com/myimage:latest")
```

## Google Container Registry (GCR)

For Google Container Registry, you can use Google Cloud credentials:

```python
from testcontainers.generic import GenericContainer

# GCR authentication using Google Cloud credentials
container = GenericContainer("gcr.io/myproject/myimage:latest")
```

## Azure Container Registry (ACR)

For Azure Container Registry, you can use Azure credentials:

```python
from testcontainers.generic import GenericContainer

# ACR authentication using Azure credentials
container = GenericContainer("myregistry.azurecr.io/myimage:latest")
```

## Best Practices

1. Never commit credentials to version control
2. Use environment variables or secure credential stores
3. Rotate credentials regularly
4. Use the least privileged credentials necessary
5. Consider using Docker credential helpers
6. Use registry-specific authentication when available
7. Keep credentials secure and encrypted
8. Use separate credentials for different environments

## Troubleshooting

If you encounter authentication issues:

1. Verify your credentials are correct
2. Check if the registry is accessible
3. Ensure your Docker daemon is running
4. Check Docker's credential store
5. Verify network connectivity
6. Check for any proxy settings
7. Look for any rate limiting
8. Check registry-specific requirements
