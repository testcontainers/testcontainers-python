# Building Images from Dockerfiles

Testcontainers-Python allows you to build Docker images from Dockerfiles during test execution. This is useful when you need to test custom images or when you want to ensure your Dockerfile builds correctly.

## Basic Image Building

The simplest way to build an image is using the `DockerImage` class. It is a context manager that builds the image on entry and removes it on exit:

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.image import DockerImage

# Build an image from a build context containing a Dockerfile
with DockerImage(path="path/to/dockerfile/directory", tag="myapp:test") as image:
    # Use the built image
    with DockerContainer(str(image)) as container:
        # Your test code here
        pass
```

`path` is the build context directory. By default the Dockerfile is expected to be named `Dockerfile` within that directory.

## Building with a Custom Dockerfile

Use `dockerfile_path` to point at a Dockerfile with a different name or location (relative to the build context):

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    dockerfile_path="Dockerfile.test",
    tag="myapp:test",
) as image:
    ...
```

## Building with Options

Any additional keyword arguments are forwarded to the underlying docker-py
[`images.build`](https://docker-py.readthedocs.io/en/stable/images.html#docker.models.images.ImageCollection.build)
call, so you can use all of its options.

### Build Arguments

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    tag="myapp:test",
    buildargs={
        "VERSION": "1.0.0",
        "ENVIRONMENT": "test",
    },
) as image:
    ...
```

### Target Stage

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    tag="myapp:test",
    target="test",
) as image:
    ...
```

### Disabling the Build Cache

Use the `no_cache` argument to bypass the build cache (equivalent to the CLI's `--no-cache`):

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    tag="myapp:test",
    no_cache=True,
) as image:
    ...
```

You can also reuse cache layers from existing images with `cache_from`:

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    tag="myapp:test",
    cache_from=["myapp:latest"],
) as image:
    ...
```

### Platform

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    tag="myapp:test",
    platform="linux/amd64",
) as image:
    ...
```

### Labels

```python
with DockerImage(
    path="path/to/dockerfile/directory",
    tag="myapp:test",
    labels={
        "test": "true",
        "environment": "test",
    },
) as image:
    ...
```

## Inspecting the Build

`DockerImage` exposes helpers to inspect the result of a build:

```python
with DockerImage(path="path/to/dockerfile/directory", tag="myapp:test") as image:
    print(image.short_id)        # short image ID
    print(str(image))            # tag if set, otherwise short ID
    logs = image.get_logs()      # list of build log entries
    wrapped = image.get_wrapped_image()  # underlying docker-py Image
```

## Cleaning Up

By default the image is removed when the context manager exits. Set `clean_up=False`
to keep the image after the block completes:

```python
with DockerImage(path="path/to/dockerfile/directory", tag="myapp:test", clean_up=False) as image:
    ...
# image is still available here
```

## Best Practices

1. Use appropriate tags
2. Clean up built images
3. Use build arguments for configuration
4. Consider build context size
5. Use appropriate build caching
6. Use appropriate platforms
7. Add meaningful labels

## Common Use Cases

### Building Test Images

```python
def test_custom_image():
    with DockerImage(
        path="path/to/dockerfile/directory",
        tag="myapp:test",
        buildargs={"TEST_MODE": "true"},
    ) as image:
        with DockerContainer(str(image)) as container:
            # Your test code here
            pass
```

### Building for Different Environments

```python
def test_different_environments():
    environments = ["dev", "test", "staging"]

    for env in environments:
        with DockerImage(
            path="path/to/dockerfile/directory",
            tag=f"myapp:{env}",
            buildargs={"ENVIRONMENT": env},
        ) as image:
            with DockerContainer(str(image)) as container:
                # Your test code here
                pass
```

## Troubleshooting

If you encounter issues with image building:

1. Check Dockerfile syntax
2. Verify the build context (the `path` argument)
3. Check for missing files
4. Verify build arguments
5. Check for platform compatibility
6. Verify cache settings
7. Verify Docker daemon state
