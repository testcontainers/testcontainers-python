import tarfile
import time
from io import BytesIO
from textwrap import dedent

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class RedpandaContainer(DockerContainer):
    """
    Redpanda container.

    Example:

        .. doctest::

            >>> from testcontainers.kafka import RedpandaContainer

            >>> with RedpandaContainer() as redpanda:
            ...    connection = redpanda.get_bootstrap_server()
    """

    TC_START_SCRIPT = "/tc-start.sh"

    def __init__(
        self,
        image: str = "docker.redpanda.com/redpandadata/redpanda:v23.1.13",
        **kwargs,
    ) -> None:
        kwargs["entrypoint"] = "sh"
        super().__init__(image, **kwargs)
        self.redpanda_port = 9092
        self.schema_registry_port = 8081
        self.with_exposed_ports(self.redpanda_port, self.schema_registry_port)

    def get_bootstrap_server(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.redpanda_port)
        return f"{host}:{port}"

    def get_schema_registry_address(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.schema_registry_port)
        return f"http://{host}:{port}"

    def tc_start(self) -> None:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.redpanda_port)

        data = (
            dedent(
                f"""
                #!/bin/bash
                /usr/bin/rpk redpanda start --mode dev-container --smp 1 --memory 1G \
                --kafka-addr PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092  \
                --advertise-kafka-addr PLAINTEXT://127.0.0.1:29092,OUTSIDE://{host}:{port}
                """
            )
            .strip()
            .encode("utf-8")
        )

        self.create_file(data, RedpandaContainer.TC_START_SCRIPT)

    def start(self, timeout=10) -> "RedpandaContainer":
        script = RedpandaContainer.TC_START_SCRIPT
        command = f'-c "while [ ! -f {script} ]; do sleep 0.1; done; sh {script}"'
        self.with_command(command)
        super().start()
        self.tc_start()
        wait_for_logs(self, r".*Started Kafka API server.*", timeout=timeout)
        return self

    def create_file(self, content: bytes, path: str) -> None:
        with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=path)
            tarinfo.size = len(content)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, BytesIO(content))
            archive.seek(0)
            self.get_wrapped_container().put_archive("/", archive)
