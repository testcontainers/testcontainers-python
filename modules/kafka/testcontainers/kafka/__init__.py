import tarfile
import time
from io import BytesIO
from textwrap import dedent

from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.kafka._redpanda import RedpandaContainer

__all__ = [
    "KafkaContainer",
    "RedpandaContainer",
]


class KafkaContainer(DockerContainer):
    """
    Kafka container.

    Example:

        .. doctest::

            >>> from testcontainers.kafka import KafkaContainer

            >>> with KafkaContainer() as kafka:
            ...    connection = kafka.get_bootstrap_server()
    """

    TC_START_SCRIPT = "/tc-start.sh"

    def __init__(self, image: str = "confluentinc/cp-kafka:7.6.0", port: int = 9093, **kwargs) -> None:
        raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)
        self.port = port
        self.with_exposed_ports(self.port)
        listeners = f"PLAINTEXT://0.0.0.0:{self.port},BROKER://0.0.0.0:9092"
        self.with_env("KAFKA_LISTENERS", listeners)
        self.with_env("KAFKA_LISTENER_SECURITY_PROTOCOL_MAP", "BROKER:PLAINTEXT,PLAINTEXT:PLAINTEXT")
        self.with_env("KAFKA_INTER_BROKER_LISTENER_NAME", "BROKER")

        self.with_env("KAFKA_BROKER_ID", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS", "1")
        self.with_env("KAFKA_LOG_FLUSH_INTERVAL_MESSAGES", "10000000")
        self.with_env("KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS", "0")

    def get_bootstrap_server(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"{host}:{port}"

    def tc_start(self) -> None:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        listeners = f"PLAINTEXT://{host}:{port},BROKER://$(hostname -i):9092"
        data = (
            dedent(
                f"""
                #!/bin/bash
                echo 'clientPort=2181' > zookeeper.properties
                echo 'dataDir=/var/lib/zookeeper/data' >> zookeeper.properties
                echo 'dataLogDir=/var/lib/zookeeper/log' >> zookeeper.properties
                zookeeper-server-start zookeeper.properties &
                export KAFKA_ZOOKEEPER_CONNECT='localhost:2181'
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
        self.with_command(command)
        super().start()
        self.tc_start()
        wait_for_logs(self, r".*\[KafkaServer id=\d+\] started.*", timeout=timeout)
        return self

    def create_file(self, content: bytes, path: str) -> None:
        with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=path)
            tarinfo.size = len(content)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, BytesIO(content))
            archive.seek(0)
            self.get_wrapped_container().put_archive("/", archive)
