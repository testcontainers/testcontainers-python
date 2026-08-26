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
from typing import Any, Optional
from urllib.request import Request, urlopen

from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy


def _control_request(url: str, method: str = "GET", body: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=5) as response:
        raw = response.read().decode()
    return json.loads(raw) if raw else {}


class ToxiproxyProxy:
    """A proxy created on a running :class:`ToxiproxyContainer`.

    Connect to the upstream *through* the proxy using :attr:`host` and
    :attr:`proxy_port`, then inject failures with :meth:`add_toxic`.
    """

    def __init__(self, name: str, host: str, proxy_port: int, control_url: str) -> None:
        self.name = name
        self.host = host
        self.proxy_port = proxy_port
        self._control_url = control_url

    def add_toxic(
        self,
        toxic_type: str,
        attributes: dict[str, Any],
        stream: str = "downstream",
        toxicity: float = 1.0,
        name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Add a toxic (e.g. ``latency``, ``bandwidth``, ``timeout``) to the proxy.

        See https://github.com/Shopify/toxiproxy#toxics for the available types
        and their attributes.
        """
        payload = {
            "name": name or f"{self.name}_{toxic_type}_{stream}",
            "type": toxic_type,
            "stream": stream,
            "toxicity": toxicity,
            "attributes": attributes,
        }
        return _control_request(f"{self._control_url}/proxies/{self.name}/toxics", "POST", payload)


class ToxiproxyContainer(DockerContainer):
    """Toxiproxy TCP proxy for simulating adverse network conditions in tests.

    Toxiproxy sits in front of another service and lets tests inject latency,
    bandwidth limits, connection drops and other failures to verify resilience.
    See https://github.com/Shopify/toxiproxy.

    Example:

    .. doctest::

        >>> from testcontainers.core.network import Network
        >>> from testcontainers.community.nginx import NginxContainer
        >>> from testcontainers.community.toxiproxy import ToxiproxyContainer

        >>> with Network() as network:
        ...     nginx = NginxContainer("nginx:alpine").with_network(network).with_network_aliases("nginx")
        ...     toxiproxy = ToxiproxyContainer().with_network(network)
        ...     with nginx, toxiproxy:
        ...         proxy = toxiproxy.create_proxy("nginx", "nginx:80")
        ...         _ = proxy.add_toxic("latency", {"latency": 1000})
    """

    CONTROL_PORT = 8474
    FIRST_PROXY_PORT = 8666
    LAST_PROXY_PORT = 8697

    def __init__(self, image: str = "ghcr.io/shopify/toxiproxy:2.11.0", **kwargs: object) -> None:
        super().__init__(image, **kwargs)
        proxy_ports = range(self.FIRST_PROXY_PORT, self.LAST_PROXY_PORT + 1)
        self.with_exposed_ports(self.CONTROL_PORT, *proxy_ports)
        self.waiting_for(HttpWaitStrategy(self.CONTROL_PORT, "/version"))
        self._next_proxy_port = self.FIRST_PROXY_PORT

    def get_control_port(self) -> int:
        """Host port mapped to the Toxiproxy HTTP control API."""
        return self.get_exposed_port(self.CONTROL_PORT)

    def get_control_url(self) -> str:
        """Base URL of the Toxiproxy HTTP control API, reachable from the host."""
        return f"http://{self.get_container_host_ip()}:{self.get_control_port()}"

    def create_proxy(self, name: str, upstream: str) -> ToxiproxyProxy:
        """Create a proxy in front of ``upstream``.

        ``upstream`` must be reachable from the Toxiproxy container itself, e.g.
        ``"host:port"`` of another container that shares a network (via
        :meth:`~testcontainers.core.container.DockerContainer.with_network_aliases`).
        Returns a :class:`ToxiproxyProxy` whose ``host``/``proxy_port`` you
        connect through instead of talking to the upstream directly.
        """
        if self._next_proxy_port > self.LAST_PROXY_PORT:
            max_proxies = self.LAST_PROXY_PORT - self.FIRST_PROXY_PORT + 1
            raise RuntimeError(f"No free proxy ports left (at most {max_proxies} proxies are supported).")
        listen_port = self._next_proxy_port
        self._next_proxy_port += 1
        _control_request(
            f"{self.get_control_url()}/proxies",
            "POST",
            {"name": name, "listen": f"0.0.0.0:{listen_port}", "upstream": upstream, "enabled": True},
        )
        return ToxiproxyProxy(
            name=name,
            host=self.get_container_host_ip(),
            proxy_port=self.get_exposed_port(listen_port),
            control_url=self.get_control_url(),
        )

    def start(self) -> Self:
        super().start()
        return self
