import json
import time

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from testcontainers.k3s import K3sContainer


def basic_example():
    with K3sContainer() as k3s:
        # Get kubeconfig
        kubeconfig = k3s.get_kubeconfig()

        # Load kubeconfig
        config.load_kube_config_from_dict(yaml.safe_load(kubeconfig))
        print("Loaded kubeconfig")

        # Create API clients
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()

        # Create namespace
        namespace = "test-namespace"
        try:
            v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace)))
            print(f"Created namespace: {namespace}")
        except ApiException as e:
            if e.status == 409:  # Already exists
                print(f"Namespace {namespace} already exists")
            else:
                raise

        # Create ConfigMap
        configmap = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(name="test-config", namespace=namespace), data={"config.yaml": "key: value"}
        )
        v1.create_namespaced_config_map(namespace=namespace, body=configmap)
        print("Created ConfigMap")

        # Create Secret
        secret = client.V1Secret(
            metadata=client.V1ObjectMeta(name="test-secret", namespace=namespace),
            type="Opaque",
            data={"username": "dGVzdA==", "password": "cGFzc3dvcmQ="},  # base64 encoded
        )
        v1.create_namespaced_secret(namespace=namespace, body=secret)
        print("Created Secret")

        # Create Deployment
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name="test-deployment", namespace=namespace),
            spec=client.V1DeploymentSpec(
                replicas=2,
                selector=client.V1LabelSelector(match_labels={"app": "test-app"}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": "test-app"}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="nginx", image="nginx:latest", ports=[client.V1ContainerPort(container_port=80)]
                            )
                        ]
                    ),
                ),
            ),
        )
        apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)
        print("Created Deployment")

        # Create Service
        service = client.V1Service(
            metadata=client.V1ObjectMeta(name="test-service", namespace=namespace),
            spec=client.V1ServiceSpec(
                selector={"app": "test-app"}, ports=[client.V1ServicePort(port=80, target_port=80)], type="ClusterIP"
            ),
        )
        v1.create_namespaced_service(namespace=namespace, body=service)
        print("Created Service")

        # Wait for pods to be ready
        print("\nWaiting for pods to be ready...")
        time.sleep(10)  # Give some time for pods to start

        # List pods
        pods = v1.list_namespaced_pod(namespace=namespace)
        print("\nPods:")
        for pod in pods.items:
            print(json.dumps({"name": pod.metadata.name, "phase": pod.status.phase, "ip": pod.status.pod_ip}, indent=2))

        # Get deployment status
        deployment_status = apps_v1.read_namespaced_deployment_status(name="test-deployment", namespace=namespace)
        print("\nDeployment status:")
        print(
            json.dumps(
                {
                    "name": deployment_status.metadata.name,
                    "replicas": deployment_status.spec.replicas,
                    "available_replicas": deployment_status.status.available_replicas,
                    "ready_replicas": deployment_status.status.ready_replicas,
                },
                indent=2,
            )
        )

        # Get service details
        service_details = v1.read_namespaced_service(name="test-service", namespace=namespace)
        print("\nService details:")
        print(
            json.dumps(
                {
                    "name": service_details.metadata.name,
                    "type": service_details.spec.type,
                    "cluster_ip": service_details.spec.cluster_ip,
                    "ports": [{"port": p.port, "target_port": p.target_port} for p in service_details.spec.ports],
                },
                indent=2,
            )
        )

        # Create Ingress
        ingress = client.V1Ingress(
            metadata=client.V1ObjectMeta(
                name="test-ingress",
                namespace=namespace,
                annotations={"nginx.ingress.kubernetes.io/rewrite-target": "/"},
            ),
            spec=client.V1IngressSpec(
                rules=[
                    client.V1IngressRule(
                        host="test.local",
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name="test-service", port=client.V1ServiceBackendPort(number=80)
                                        )
                                    ),
                                )
                            ]
                        ),
                    )
                ]
            ),
        )
        networking_v1 = client.NetworkingV1Api()
        networking_v1.create_namespaced_ingress(namespace=namespace, body=ingress)
        print("\nCreated Ingress")

        # Get ingress details
        ingress_details = networking_v1.read_namespaced_ingress(name="test-ingress", namespace=namespace)
        print("\nIngress details:")
        print(
            json.dumps(
                {
                    "name": ingress_details.metadata.name,
                    "host": ingress_details.spec.rules[0].host,
                    "path": ingress_details.spec.rules[0].http.paths[0].path,
                },
                indent=2,
            )
        )

        # Clean up
        print("\nCleaning up resources...")
        networking_v1.delete_namespaced_ingress(name="test-ingress", namespace=namespace)
        v1.delete_namespaced_service(name="test-service", namespace=namespace)
        apps_v1.delete_namespaced_deployment(name="test-deployment", namespace=namespace)
        v1.delete_namespaced_secret(name="test-secret", namespace=namespace)
        v1.delete_namespaced_config_map(name="test-config", namespace=namespace)
        v1.delete_namespace(name=namespace)


if __name__ == "__main__":
    basic_example()
