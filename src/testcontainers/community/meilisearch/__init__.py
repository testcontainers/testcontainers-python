import os
import secrets
from typing import Optional

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy


class MeilisearchContainer(DockerContainer):
    """
    Meilisearch container.

    Example:

        .. doctest::

            >>> from meilisearch import Client
            >>> from testcontainers.community.meilisearch import MeilisearchContainer

            >>> with MeilisearchContainer() as meili:
            ...     client = Client(meili.get_connection_url(), meili.get_master_key())
            ...     client.health()["status"]
            'available'
    """

    def __init__(
        self,
        image: str = "getmeili/meilisearch:v1.53",
        port: int = 7700,
        meili_env: Optional[str] = None,
        master_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image=image, **kwargs)

        self.port = port
        self.meili_env = meili_env or os.environ.get("MEILI_ENV", "production")
        self.master_key = master_key or os.environ.get("MEILI_MASTER_KEY", secrets.token_urlsafe(32))

        if self.meili_env == "production" and len(self.master_key.encode()) < 16:
            raise ValueError("master key must be at least 16 bytes when MEILI_ENV=production")

        self.with_exposed_ports(self.port)
        self.with_env("MEILI_ENV", self.meili_env)
        self.with_env("MEILI_MASTER_KEY", self.master_key)
        self.with_env("MEILI_NO_ANALYTICS", "true")

        self.waiting_for(HttpWaitStrategy(self.port, "/health"))

    def get_master_key(self) -> str:
        return self.master_key

    def get_connection_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"
