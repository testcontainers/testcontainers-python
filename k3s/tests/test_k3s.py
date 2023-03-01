# The versions below were the current supported versions at time of writing (2022-08-11)

from testcontainers.k3s import K3SContainer


def test_docker_run_elasticsearch():
    with K3SContainer() as k3s:
        exposed_port = k3s.get_exposed_port(k3s.KUBE_SECURE_PORT)
        server_url_in_config_yaml = 'https://localhost:{}'.format(exposed_port)
        assert server_url_in_config_yaml in k3s.config_yaml()
