# Building Images from Dockerfiles

Testcontainers-Python allows you to build Docker images from Dockerfiles during test execution. This is useful when you need to test custom images or when you want to ensure your Dockerfile builds correctly.

## Basic Image Building

The simplest way to build an image is using the `build_image` function:

```python
from testcontainers.core.container import build_image

# Build an image from a Dockerfile
image = build_image(
    path="path/to/dockerfile/directory",
    tag="myapp:test"
)

# Use the built image
with GenericContainer(image) as container:
    # Your test code here
    pass
```

## Building with Options

You can customize the build process with various options:

```python
# Build with specific Dockerfile
image = build_image(
    path="path/to/dockerfile/directory",
    dockerfile="Dockerfile.test",
    tag="myapp:test"
)

# Build with build arguments
image = build_image(
    path="path/to/dockerfile/directory",
    buildargs={
        "VERSION": "1.0.0",
        "ENVIRONMENT": "test"
    },
    tag="myapp:test"
)

# Build with target stage
image = build_image(
    path="path/to/dockerfile/directory",
    target="test",
    tag="myapp:test"
)
```

## Building with Context

You can specify a build context:

```python
# Build with specific context
image = build_image(
    path="path/to/dockerfile/directory",
    context="path/to/build/context",
    tag="myapp:test"
)
```

## Building with Cache

You can control build caching:

```python
# Build without cache
image = build_image(
    path="path/to/dockerfile/directory",
    nocache=True,
    tag="myapp:test"
)

# Build with specific cache from
image = build_image(
    path="path/to/dockerfile/directory",
    cache_from=["myapp:latest"],
    tag="myapp:test"
)
```

## Building with Platform

You can specify the target platform:

```python
# Build for specific platform
image = build_image(
    path="path/to/dockerfile/directory",
    platform="linux/amd64",
    tag="myapp:test"
)
```

## Building with Labels

You can add labels to the built image:

```python
# Build with labels
image = build_image(
    path="path/to/dockerfile/directory",
    labels={
        "test": "true",
        "environment": "test"
    },
    tag="myapp:test"
)
```

## Best Practices

1. Use appropriate tags
2. Clean up built images
3. Use build arguments for configuration
4. Consider build context size
5. Use appropriate build caching
6. Handle build failures
7. Use appropriate platforms
8. Add meaningful labels

## Common Use Cases

### Building Test Images

```python
def test_custom_image():
    # Build test image
    image = build_image(
        path="path/to/dockerfile/directory",
        buildargs={"TEST_MODE": "true"},
        tag="myapp:test"
    )

    # Use the test image
    with GenericContainer(image) as container:
        # Your test code here
        pass
```

### Building with Dependencies

```python
def test_with_dependencies():
    # Build base image
    base_image = build_image(
        path="path/to/base/dockerfile/directory",
        tag="myapp:base"
    )

    # Build test image using base
    test_image = build_image(
        path="path/to/test/dockerfile/directory",
        cache_from=[base_image],
        tag="myapp:test"
    )
```

### Building for Different Environments

```python
def test_different_environments():
    # Build for different environments
    environments = ["dev", "test", "staging"]

    for env in environments:
        image = build_image(
            path="path/to/dockerfile/directory",
            buildargs={"ENVIRONMENT": env},
            tag=f"myapp:{env}"
        )
```

## Troubleshooting

If you encounter issues with image building:

1. Check Dockerfile syntax
2. Verify build context
3. Check for missing files
4. Verify build arguments
5. Check for platform compatibility
6. Verify cache settings
7. Check for resource limits
8. Verify Docker daemon state
