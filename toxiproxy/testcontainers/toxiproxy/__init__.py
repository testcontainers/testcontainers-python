from typing import List, Optional, Set
from testcontainers.core.container import DockerContainer
from toxiproxy.server import Toxiproxy
from toxiproxy.proxy import Proxy


class ToxiProxyContainer(DockerContainer):
    def __init__(self, additional_ports: List[int],
                 image: str = 'ghcr.io/shopify/toxiproxy',
                 listen_host: str = '0.0.0.0', listen_port: int = 8474) -> None:
        super().__init__(image)
        self.toxiproxy_server: Optional[Toxiproxy] = None
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.additional_ports: Set[int] = set(additional_ports)
        self.used_ports: Set[int] = set()

        # Bind specified listen port for the ToxiProxy REST API
        self.with_bind_ports(container=self.listen_port, host=self.listen_port)

        # Bind additional ports
        for port in self.additional_ports:
            self.with_bind_ports(container=port, host=port)

    def start(self) -> 'ToxiProxyContainer':
        super().start()
        self.init_toxiproxy_server()
        return self

    def init_toxiproxy_server(self) -> None:
        self.toxiproxy_server = Toxiproxy()
        self.toxiproxy_server.update_api_consumer(host=self.listen_host, port=self.listen_port)

    def stop(self) -> None:
        self.reset_toxiproxy_server()
        super().stop()

    def reset_toxiproxy_server(self) -> None:
        self.used_ports.clear()
        self.toxiproxy_server.reset()
        self.toxiproxy_server.destroy_all()
        # Additional cleanup as needed

    def create_proxy(self, name: str, upstream_host: str, upstream_port: int,
                     listen_host: Optional[str] = '0.0.0.0', listen_port: Optional[int] = None,
                     enabled=True) -> Proxy:
        if listen_port:
            if listen_port in self.used_ports:
                raise Exception(f'Port {listen_port} is already in use.')
            elif listen_port not in self.additional_ports:
                raise Exception(f'Port {listen_port} is not among the additional ports.')
        else:
            listen_port = self.get_available_port()
            if listen_port is None:
                raise Exception('No available ports.')

        listen = f'{listen_host}:{listen_port}'
        upstream = f'{upstream_host}:{upstream_port}'
        proxy = self.toxiproxy_server.create(
            name=name, listen=listen, upstream=upstream, enabled=enabled)
        self.used_ports.add(listen_port)
        return proxy

    def remove_proxy(self, proxy: Proxy) -> None:
        self.used_ports.discard(proxy.get_listen_port())
        proxy.destroy()

    def get_available_port(self) -> Optional[int]:
        for port in self.additional_ports:
            if port not in self.used_ports:
                return port
        return None
