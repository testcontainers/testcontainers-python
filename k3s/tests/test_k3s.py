# The versions below were the current supported versions at time of writing (2022-08-11)
import yaml
from kubernetes import client, config

from testcontainers.k3s import K3SContainer


def test_docker_run_k3s():
    with K3SContainer() as k3s:
        config.load_kube_config_from_dict(yaml.safe_load(k3s.config_yaml()))
        pod = client.CoreV1Api().list_pod_for_all_namespaces(limit=1)
        assert len(pod.items) > 0, "Unable to get running nodes from k3s cluster"
