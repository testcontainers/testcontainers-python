import requests

from testcontainers.nginx import NginxContainer


def test_docker_run_nginx():
    nginx_container = NginxContainer("nginx:1.13.8")
    with nginx_container as nginx:
        port = nginx.port_to_expose
        url = "http://{}:{}/".format(nginx.get_container_host_ip(),
                                     nginx.get_exposed_port(port))
        r = requests.get(url)
        assert (r.status_code == 200)
        assert ('Welcome to nginx!' in r.text)
