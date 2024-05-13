from typing import Optional

import httpx

from testcontainers.core.generic import SrvContainer


class FastAPIContainer(SrvContainer):
    """
    FastAPI container that is based on a custom image.

    Example:

        .. doctest::

            >>> from testcontainers.fastapi import FastAPIContainer
            >>> from testcontainers.core.waiting_utils import wait_for_logs

            >>> with FastAPIContainer(path="./modules/fastapi/tests/sample", port=80, tag="fastapi:latest") as fastapi:
            ...     delay = wait_for_logs(fastapi, "Uvicorn running on http://0.0.0.0:80")
            ...     client = fastapi.get_client()
            ...     response = client.get("/")
            ...     assert response.status_code == 200
            ...     assert response.json() == {"Status": "Working"}
    """

    def __init__(self, path: str, port: int, tag: Optional[str] = None, image_cleanup: bool = True) -> None:
        """
        :param path: Path to the FastAPI application.
        :param port: Port to expose the FastAPI application.
        :param tag: Tag for the image to be built (default: None).
        :param image_cleanup: Clean up the image after the container is stopped (default: True).
        """
        super().__init__(path, port, tag, image_cleanup)

    def get_api_url(self) -> str:
        return self._create_connection_url() + "/api/v1/"

    def get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self.get_api_url())

    def get_stdout(self) -> str:
        return self.get_logs()[0].decode("utf-8")
