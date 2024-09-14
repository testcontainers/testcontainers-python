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


def test_docker_container_with_env_file():
    """Test that environment variables can be loaded from a file"""
    with tempfile.TemporaryDirectory() as temp_directory:
        env_file_path = Path(temp_directory) / "env_file"
        with open(env_file_path, "w") as f:
            f.write(
                """
                TEST_ENV_VAR=hello
                NUMBER=123
                DOMAIN=example.org
                ADMIN_EMAIL=admin@${DOMAIN}
                ROOT_URL=${DOMAIN}/app
                """
            )
        container = DockerContainer("alpine").with_command("tail -f /dev/null")  # Keep the container running
        container.with_env_file(env_file_path)  # Load the environment variables from the file
        with container:
            output = container.exec("env").output.decode("utf-8").strip()
            assert "TEST_ENV_VAR=hello" in output
            assert "NUMBER=123" in output
            assert "DOMAIN=example.org" in output
            assert "ADMIN_EMAIL=admin@example.org" in output
            assert "ROOT_URL=example.org/app" in output
            print(output)
