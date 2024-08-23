from testcontainers.core.container import DockerContainer


def test_garbage_collection_is_defensive():
    # For more info, see https://github.com/testcontainers/testcontainers-python/issues/399
    # we simulate garbage collection: start, stop, then call `del`
    container = DockerContainer("postgres:latest")
    container.start()
    container.stop(force=True, delete_volume=True)
    delattr(container, "_container")
    del container


def test_get_logs():
    with DockerContainer("hello-world") as container:
        stdout, stderr = container.get_logs()
        assert isinstance(stdout, bytes)
        assert isinstance(stderr, bytes)
        assert "Hello from Docker".encode() in stdout, "There should be something on stdout"
