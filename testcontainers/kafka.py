import tarfile
import time
from io import BytesIO
from textwrap import dedent

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class KafkaContainer(DockerContainer):
    KAFKA_PORT = 9093
    TC_START_SCRIPT = '/tc-start.sh'

    def __init__(self, image="confluentinc/cp-kafka:5.4.3", port_to_expose=KAFKA_PORT):
        super(KafkaContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        listeners = 'PLAINTEXT://0.0.0.0:{},BROKER://0.0.0.0:9092'.format(port_to_expose)
        self.with_env('KAFKA_LISTENERS', listeners)
        self.with_env('KAFKA_LISTENER_SECURITY_PROTOCOL_MAP',
                      'BROKER:PLAINTEXT,PLAINTEXT:PLAINTEXT')
        self.with_env('KAFKA_INTER_BROKER_LISTENER_NAME', 'BROKER')

        self.with_env('KAFKA_BROKER_ID', '1')
        self.with_env('KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR', '1')
        self.with_env('KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS', '1')
        self.with_env('KAFKA_LOG_FLUSH_INTERVAL_MESSAGES', '10000000')
        self.with_env('KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS', '0')

    def get_bootstrap_server(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return '{}:{}'.format(host, port)

    @wait_container_is_ready()
    def _connect(self):
        bootstrap_server = self.get_bootstrap_server()
        consumer = KafkaConsumer(group_id='test', bootstrap_servers=[bootstrap_server])
        if not consumer.topics():
            raise KafkaError("Unable to connect with kafka container!")

    def tc_start(self):
        port = self.get_exposed_port(self.port_to_expose)
        listeners = 'PLAINTEXT://localhost:{},BROKER://$(hostname -i):9092'.format(port)
        data = (
            dedent(
                """
                #!/bin/bash
                echo 'clientPort=2181' > zookeeper.properties
                echo 'dataDir=/var/lib/zookeeper/data' >> zookeeper.properties
                echo 'dataLogDir=/var/lib/zookeeper/log' >> zookeeper.properties
                zookeeper-server-start zookeeper.properties &
                export KAFKA_ZOOKEEPER_CONNECT='localhost:2181'
                export KAFKA_ADVERTISED_LISTENERS={}
                . /etc/confluent/docker/bash-config
                /etc/confluent/docker/configure
                /etc/confluent/docker/launch
                """.format(listeners)
            )
            .strip()
            .encode('utf-8')
        )
        self.create_file(data, KafkaContainer.TC_START_SCRIPT)

    def start(self):
        script = KafkaContainer.TC_START_SCRIPT
        command = 'sh -c "while [ ! -f {} ]; do sleep 0.1; done; sh {}"'.format(script, script)
        self.with_command(command)
        super().start()
        self.tc_start()
        self._connect()
        return self

    def create_file(self, content: bytes, path: str):
        with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=path)
            tarinfo.size = len(content)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, BytesIO(content))
            archive.seek(0)
            self.get_wrapped_container().put_archive("/", archive)
