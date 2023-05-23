import requests
from testcontainers.core.waiting_utils import wait_for_logs

from testcontainers.nginx import NginxContainer


def test_docker_run_nginx():
    with NginxContainer("nginx:1.24.0") as nginx:
        wait_for_logs(nginx, 'ready for start up')
        url = f"http://{nginx.get_container_host_ip()}:{nginx.get_exposed_port(nginx.port)}/"
        r = requests.get(url)
        assert (r.status_code == 200)
        assert ('Welcome to nginx!' in r.text)
