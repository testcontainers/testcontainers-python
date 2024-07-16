import tarfile
import time
from dataclasses import dataclass, field
from io import BytesIO
from os import environ
from textwrap import dedent

from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.version import ComparableVersion
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.kafka._redpanda import RedpandaContainer

__all__ = [
    "KafkaContainer",
    "RedpandaContainer",
    "kafka_config",
]
LIMIT_BROKER_ENV_VAR = "TC_KAFKA_LIMIT_BROKER_TO_FIRST_HOST"


@dataclass
class _KafkaConfig:
    limit_broker_to_first_host: bool = field(default_factory=lambda: environ.get(LIMIT_BROKER_ENV_VAR) == "true")
    """
    This option is useful for a setup with a network,
    see testcontainers/testcontainers-python#637 for more details
    """


kafka_config = _KafkaConfig()


class KafkaContainer(DockerContainer):
    """
    Kafka container.

    Example:

        .. doctest::

            >>> from testcontainers.kafka import KafkaContainer

            >>> with KafkaContainer() as kafka:
            ...    connection = kafka.get_bootstrap_server()

            # Using KRaft protocol
            >>> with KafkaContainer().with_kraft() as kafka:
            ...    connection = kafka.get_bootstrap_server()
    """

    TC_START_SCRIPT = "/tc-start.sh"
    MIN_KRAFT_TAG = "7.0.0"

    def __init__(self, image: str = "confluentinc/cp-kafka:7.6.0", port: int = 9093, **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.kraft_enabled = False
        self.wait_for = r".*\[KafkaServer id=\d+\] started.*"
        self.boot_command = ""
        self.cluster_id = "MkU3OEVBNTcwNTJENDM2Qk"
        self.listeners = f"PLAINTEXT://0.0.0.0:{self.port},BROKER://0.0.0.0:9092"
        self.security_protocol_map = "BROKER:PLAINTEXT,PLAINTEXT:PLAINTEXT"

        self.with_exposed_ports(self.port)
        self.with_env("KAFKA_LISTENERS", self.listeners)
        self.with_env("KAFKA_LISTENER_SECURITY_PROTOCOL_MAP", self.security_protocol_map)
        self.with_env("KAFKA_INTER_BROKER_LISTENER_NAME", "BROKER")

        self.with_env("KAFKA_BROKER_ID", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS", "1")
        self.with_env("KAFKA_LOG_FLUSH_INTERVAL_MESSAGES", "10000000")
        self.with_env("KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS", "0")

    def with_kraft(self) -> Self:
        self._verify_min_kraft_version()
        self.kraft_enabled = True
        return self

    def _verify_min_kraft_version(self):
        actual_version = self.image.split(":")[-1]

        if ComparableVersion(actual_version) < self.MIN_KRAFT_TAG:
            raise ValueError(
                f"Provided Confluent Platform's version {actual_version} "
                f"is not supported in Kraft mode"
                f" (must be {self.MIN_KRAFT_TAG} or above)"
            )

    def with_cluster_id(self, cluster_id: str) -> Self:
        self.cluster_id = cluster_id
        return self

    def configure(self):
        if self.kraft_enabled:
            self._configure_kraft()
        else:
            self._configure_zookeeper()

    def _configure_kraft(self) -> None:
        self.wait_for = r".*Kafka Server started.*"

        self.with_env("CLUSTER_ID", self.cluster_id)
        self.with_env("KAFKA_NODE_ID", 1)
        self.with_env(
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP",
            f"{self.security_protocol_map},CONTROLLER:PLAINTEXT",
        )
        self.with_env(
            "KAFKA_LISTENERS",
            f"{self.listeners},CONTROLLER://0.0.0.0:9094",
        )
        self.with_env("KAFKA_PROCESS_ROLES", "broker,controller")

        network_alias = self._get_network_alias()
        controller_quorum_voters = f"1@{network_alias}:9094"
        self.with_env("KAFKA_CONTROLLER_QUORUM_VOTERS", controller_quorum_voters)
        self.with_env("KAFKA_CONTROLLER_LISTENER_NAMES", "CONTROLLER")

        self.boot_command = f"""
                    sed -i '/KAFKA_ZOOKEEPER_CONNECT/d' /etc/confluent/docker/configure
                    echo 'kafka-storage format --ignore-formatted -t {self.cluster_id} -c /etc/kafka/kafka.properties' >> /etc/confluent/docker/configure
                """

    def _get_network_alias(self):
        if self._network:
            return next(
                iter(self._network_aliases or [self._network.name or self._kwargs.get("network", [])]),
                None,
            )

        return "localhost"

    def _configure_zookeeper(self) -> None:
        self.boot_command = """
                echo 'clientPort=2181' > zookeeper.properties
                echo 'dataDir=/var/lib/zookeeper/data' >> zookeeper.properties
                echo 'dataLogDir=/var/lib/zookeeper/log' >> zookeeper.properties
                zookeeper-server-start zookeeper.properties &
                export KAFKA_ZOOKEEPER_CONNECT='localhost:2181'
        """

    def get_bootstrap_server(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"{host}:{port}"

    def tc_start(self) -> None:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        if kafka_config.limit_broker_to_first_host:
            listeners = f"PLAINTEXT://{host}:{port},BROKER://$(hostname -i | cut -d' ' -f1):9092"
        else:
            listeners = f"PLAINTEXT://{host}:{port},BROKER://$(hostname -i):9092"
        data = (
            dedent(
                f"""
                #!/bin/bash
                {self.boot_command}
                export KAFKA_ADVERTISED_LISTENERS={listeners}
                . /etc/confluent/docker/bash-config
                /etc/confluent/docker/configure
                /etc/confluent/docker/launch
                """
            )
            .strip()
            .encode("utf-8")
        )
        self.create_file(data, KafkaContainer.TC_START_SCRIPT)

    def start(self, timeout=30) -> "KafkaContainer":
        script = KafkaContainer.TC_START_SCRIPT
        command = f'sh -c "while [ ! -f {script} ]; do sleep 0.1; done; sh {script}"'
        self.configure()
        self.with_command(command)
        super().start()
        self.tc_start()
        wait_for_logs(self, self.wait_for, timeout=timeout)
        return self

    def create_file(self, content: bytes, path: str) -> None:
        with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=path)
            tarinfo.size = len(content)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, BytesIO(content))
            archive.seek(0)
            self.get_wrapped_container().put_archive("/", archive)
