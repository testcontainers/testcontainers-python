import time

import requests

from testcontainers.community.nginx import NginxContainer
from testcontainers.community.toxiproxy import ToxiproxyContainer
from testcontainers.core.network import Network


def latency_example():
    with Network() as network:
        # An upstream service and Toxiproxy share a network so Toxiproxy can reach it.
        nginx = NginxContainer("nginx:alpine").with_network(network).with_network_aliases("nginx")
        toxiproxy = ToxiproxyContainer().with_network(network)
        with nginx, toxiproxy:
            # Route traffic to the upstream "nginx:80" through Toxiproxy.
            proxy = toxiproxy.create_proxy("nginx", "nginx:80")
            url = f"http://{proxy.host}:{proxy.proxy_port}/"

            print(f"Status without toxics: {requests.get(url).status_code}")

            # Inject 1 second of downstream latency.
            proxy.add_toxic("latency", {"latency": 1000})

            start = time.monotonic()
            requests.get(url)
            print(f"Request took {time.monotonic() - start:.2f}s with the latency toxic")


if __name__ == "__main__":
    latency_example()
