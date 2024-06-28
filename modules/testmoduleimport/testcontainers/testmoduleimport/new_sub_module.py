from testcontainers.generic.server import ServerContainer


class NewSubModuleContainer(ServerContainer):
    """
    This class is a mock container for testing purposes. It is used to test importing from other modules.

    .. doctest::

        >>> import httpx
        >>> from testcontainers.core.image import DockerImage
        >>> from testcontainers.testmoduleimport import NewSubModuleContainer

        >>> with DockerImage(path="./modules/generic/tests/samples/python_server", tag="test-mod:latest") as image:
        ...     with NewSubModuleContainer(port=9000, image=image) as srv:
        ...         url = srv._create_connection_url()
        ...         response = httpx.get(f"{url}", timeout=5)
        ...         assert response.status_code == 200, "Response status code is not 200"
        ...         assert srv.print_mock() == "NewSubModuleContainer"

    """

    def __init__(self, port: int, image: str) -> None:
        super().__init__(port, image)

    def print_mock(self) -> str:
        return "NewSubModuleContainer"
