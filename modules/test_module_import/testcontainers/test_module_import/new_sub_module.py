from testcontainers.generic.server import ServerContainer


class NewSubModuleContainer(ServerContainer):
    """
    This class is a mock container for testing purposes. It is used to test importing from other modules.

    .. doctest::

        >>> import httpx
        >>> from testcontainers.core.image import DockerImage
        >>> from testcontainers.test_module_import import NewSubModuleContainer

        >>> with DockerImage(path="./modules/generic/tests/samples/python_server", tag="test-new-mod:latest") as image:
        ...     with NewSubModuleContainer(port=9000, image=image) as new_mod:
        ...         url = new_mod._create_connection_url()
        ...         response = httpx.get(f"{url}", timeout=5)
        ...         assert response.status_code == 200, "Response status code is not 200"
        ...         assert new_mod.additional_capability() == "NewSubModuleContainer"

    """

    def __init__(self, port: int, image: str) -> None:
        super().__init__(port, image)

    def additional_capability(self) -> str:
        return "NewSubModuleContainer"
