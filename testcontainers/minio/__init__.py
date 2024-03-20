from typing import TYPE_CHECKING

from requests import ConnectionError, get

from minio import Minio
from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready

if TYPE_CHECKING:
    from requests import Response


class MinioContainer(DockerContainer):
    """
    The example below spins up an Minio container and creates a new bucket in it.
    Furthermore, it demonstrates how an object is written to this bucket and
    then subsequently retrieved.
    The method :code:`get_client` can be used to create a client for the Minio Python API.
    The method :code:`get_config` can be used to retrieve the endpoint, access key
    and secret key of the container.

    Example:

        .. doctest::

            >>> import io
            >>> from testcontainers.minio import MinioContainer

            >>> with MinioContainer() as minio:
            ...   client = minio.get_client()
            ...   client.make_bucket("test")
            ...   test_content = b"Hello World"
            ...   write_result = client.put_object(
            ...       "test",
            ...       "testfile.txt",
            ...       io.BytesIO(test_content),
            ...       length=len(test_content),
            ...   )
            ...   retrieved_content = client.get_object("test", "testfile.txt").data
    """

    def __init__(
        self,
        image: str = "minio/minio:RELEASE.2022-12-02T19-19-22Z",
        port: int = 9000,
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        **kwargs,
    ) -> None:
        """
        Args:
            image: Docker image to use for the MinIO container.
            port: Port to expose on the container.
            access_key: Access key for client connections.
            secret_key: Secret key for client connections.
        """
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.access_key = access_key
        self.secret_key = secret_key

        self.with_exposed_ports(self.port)
        self.with_env("MINIO_ACCESS_KEY", self.access_key)
        self.with_env("MINIO_SECRET_KEY", self.secret_key)
        self.with_command(f"server /data --address :{self.port}")

    def get_client(self, **kwargs) -> Minio:
        """Returns a Minio client to connect to the container.

        Returns:
            Minio: Python Minio Client according to
                   https://min.io/docs/minio/linux/developers/python/API.html
        """
        host_ip = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.port)
        return Minio(
            f"{host_ip}:{exposed_port}",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
            **kwargs,
        )

    def get_config(self) -> dict:
        """This method returns the configuration of the Minio container,
        including the endpoint, access key, and secret key.

        Returns:
            dict: {`endpoint`: str, `access_key`: str, `secret_key`: str}
        """
        host_ip = self.get_container_host_ip()
        exposed_port = self.get_exposed_port(self.port)
        return {
            "endpoint": f"{host_ip}:{exposed_port}",
            "access_key": self.access_key,
            "secret_key": self.secret_key,
        }

    @wait_container_is_ready(ConnectionError)
    def _healthcheck(self) -> None:
        """This is an internal method used to check if the Minio container
        is healthy and ready to receive requests."""
        url = f"http://{self.get_config()['endpoint']}/minio/health/live"
        response: Response = get(url)
        response.raise_for_status()

    def start(self) -> "MinioContainer":
        """This method starts the Minio container and runs the healthcheck
        to verify that the container is ready to use."""
        super().start()
        self._healthcheck()
        return self
