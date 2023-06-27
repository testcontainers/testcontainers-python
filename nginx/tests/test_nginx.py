import requests

from testcontainers.nginx import NginxContainer


def test_docker_run_nginx():
    with NginxContainer("nginx:1.24.0") as nginx:
        url = f"http://{nginx.get_container_host_ip()}:{nginx.get_exposed_port(nginx.port)}/"
        r = requests.get(url)
        assert (r.status_code == 200)
        assert ('Welcome to nginx!' in r.text)
