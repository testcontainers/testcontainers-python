import time

import requests

from testcontainers.community.nginx import NginxContainer
from testcontainers.community.toxiproxy import ToxiproxyContainer
from testcontainers.core.network import Network


def test_toxiproxy_proxies_traffic_and_injects_latency():
    with Network() as network:
        nginx = NginxContainer("nginx:alpine").with_network(network).with_network_aliases("nginx")
        toxiproxy = ToxiproxyContainer().with_network(network)
        with nginx, toxiproxy:
            proxy = toxiproxy.create_proxy("nginx", "nginx:80")
            url = f"http://{proxy.host}:{proxy.proxy_port}/"

            # Traffic flows through the proxy to the upstream nginx.
            response = requests.get(url, timeout=10)
            assert response.status_code == 200
            assert "nginx" in response.text.lower()

            # Injecting 1s of downstream latency slows the response down.
            proxy.add_toxic("latency", {"latency": 1000})
            start = time.monotonic()
            assert requests.get(url, timeout=10).status_code == 200
            assert time.monotonic() - start >= 1.0


def test_create_proxy_runs_out_of_ports():
    toxiproxy = ToxiproxyContainer()
    with toxiproxy:
        # Exhaust the available proxy port range without a real upstream; the
        # control API happily registers proxies pointing at an unused address.
        for i in range(ToxiproxyContainer.FIRST_PROXY_PORT, ToxiproxyContainer.LAST_PROXY_PORT + 1):
            toxiproxy.create_proxy(f"p{i}", "example:1234")
        try:
            toxiproxy.create_proxy("one-too-many", "example:1234")
            raise AssertionError("expected RuntimeError when out of proxy ports")
        except RuntimeError:
            pass
