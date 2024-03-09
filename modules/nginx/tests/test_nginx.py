import requests

from testcontainers.nginx import NginxContainer


def test_docker_run_nginx():
    nginx_container = NginxContainer("nginx:1.13.8")
    with nginx_container as nginx:
        url = f"http://{nginx.get_container_host_ip()}:{nginx.get_exposed_port(nginx.port)}/"
        r = requests.get(url)
        assert r.status_code == 200
        assert "Welcome to nginx!" in r.text
