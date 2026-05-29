#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
from http.client import HTTPException
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class N8nContainer(DockerContainer):
    """
    n8n workflow automation container.

    Starts an n8n instance, sets up the owner account, and generates an API key
    for programmatic access via the public API.

    Example:

        .. doctest::

            >>> from testcontainers.n8n import N8nContainer

            >>> with N8nContainer() as n8n:
            ...     api_key = n8n.get_api_key()
            ...     assert api_key is not None
    """

    def __init__(
        self,
        image: str = "docker.n8n.io/n8nio/n8n:latest",
        port: int = 5678,
        owner_email: str = "owner@test.com",
        owner_password: str = "Testpass1",
        owner_first_name: str = "Test",
        owner_last_name: str = "User",
        encryption_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        self.port = port
        self.owner_email = owner_email
        self.owner_password = owner_password
        self.owner_first_name = owner_first_name
        self.owner_last_name = owner_last_name
        self.encryption_key = encryption_key
        self._api_key: Optional[str] = None
        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("N8N_PORT", str(self.port))
        self.with_env("N8N_DIAGNOSTICS_ENABLED", "false")
        self.with_env("N8N_SECURE_COOKIE", "false")
        if self.encryption_key:
            self.with_env("N8N_ENCRYPTION_KEY", self.encryption_key)

    def get_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"

    def get_webhook_url(self) -> str:
        return f"{self.get_url()}/webhook-test"

    def get_api_key(self) -> str:
        """Return the API key for the public API (X-N8N-API-KEY header)."""
        if self._api_key is None:
            raise RuntimeError("API key not available. Is the container started?")
        return self._api_key

    @wait_container_is_ready(HTTPException, URLError, ConnectionError, json.JSONDecodeError)
    def _healthcheck(self) -> None:
        # /healthz returns 200 before the REST API is fully initialized,
        # so we check /rest/settings which only returns valid JSON once ready.
        url = f"{self.get_url()}/rest/settings"
        with urlopen(url, timeout=5) as res:
            if res.status > 299:
                raise HTTPException()
            body = res.read().decode()
            json.loads(body)

    def _post_json(self, path: str, data: dict, headers: Optional[dict] = None) -> tuple:
        """Make a JSON POST request, return (parsed_body, response_headers)."""
        payload = json.dumps(data).encode()
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        req = Request(
            f"{self.get_url()}{path}",
            data=payload,
            headers=req_headers,
            method="POST",
        )
        with urlopen(req, timeout=10) as res:
            body = json.loads(res.read().decode())
            return body, res.headers

    def _setup_owner_and_api_key(self) -> str:
        """Set up the owner account, create an API key, and return it."""
        # Step 1: Create owner — returns session cookie
        _, setup_headers = self._post_json(
            "/rest/owner/setup",
            {
                "email": self.owner_email,
                "firstName": self.owner_first_name,
                "lastName": self.owner_last_name,
                "password": self.owner_password,
            },
        )
        cookie = setup_headers.get("Set-Cookie", "").split(";")[0]

        # Step 2: Get available API key scopes for the owner role
        req = Request(
            f"{self.get_url()}/rest/api-keys/scopes",
            headers={"Cookie": cookie},
        )
        with urlopen(req, timeout=10) as res:
            scopes = json.loads(res.read().decode())["data"]

        # Step 3: Create API key with all available scopes
        body, _ = self._post_json(
            "/rest/api-keys",
            {
                "label": "testcontainer",
                "scopes": scopes,
                "expiresAt": 2089401600000,
            },
            headers={"Cookie": cookie},
        )

        return body["data"]["rawApiKey"]

    def start(self) -> "N8nContainer":
        super().start()
        self._healthcheck()
        self._api_key = self._setup_owner_and_api_key()
        return self
