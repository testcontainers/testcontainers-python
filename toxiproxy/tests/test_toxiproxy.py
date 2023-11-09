from testcontainers.toxiproxy import ToxiProxyContainer
from testcontainers.core.waiting_utils import wait_for_logs


def test_docker_run_toxiproxy():
    start_port = 5570
    end_port = 5600

    # start a toxiproxy server in a container
    toxiproxy_container = (
        ToxiProxyContainer(additional_ports=range(start_port, end_port))
    ).start()

    # Wait for the toxiproxy HTTP server to start up and verify that is working
    wait_for_logs(toxiproxy_container, 'Starting Toxiproxy HTTP server')
    assert toxiproxy_container.toxiproxy_server.running() == True
    available_port = toxiproxy_container.get_available_port()
    assert available_port in range(start_port, end_port)
    proxy_name = 'test'
    proxy = toxiproxy_container.create_proxy(
        name=proxy_name,
        upstream_host='host.docker.internal',
        upstream_port=end_port,
    )
    assert proxy.destroy() == True
    assert proxy.destroy() == False
