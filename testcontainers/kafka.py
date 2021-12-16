from kafka import KafkaConsumer
from kafka.errors import KafkaError, UnrecognizedBrokerVersion, NoBrokersAvailable

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class KafkaContainer(DockerContainer):
    KAFKA_PORT = 9093

    def __init__(self, image="confluentinc/cp-kafka:5.4.3", port_to_expose=KAFKA_PORT):
        super(KafkaContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)

        env = {
            'KAFKA_LISTENERS': f'PLAINTEXT://0.0.0.0:{port_to_expose},BROKER://0.0.0.0:9092',
            'KAFKA_LISTENER_SECURITY_PROTOCOL_MAP': 'BROKER:PLAINTEXT,PLAINTEXT:PLAINTEXT',
            'KAFKA_INTER_BROKER_LISTENER_NAME': 'BROKER',
            'KAFKA_BROKER_ID': '1',
            'KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR': '1',
            'KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS': '1',
            'KAFKA_LOG_FLUSH_INTERVAL_MESSAGES': '10000000',
            'KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS': '0',
            'KAFKA_ZOOKEEPER_CONNECT': 'localhost:2181',
        }
        for key, value in env.items():
            self.with_env(key, value)

        # Start zookeeper first because it doesn't need any port mapping information.
        self.with_command("zookeeper-server-start /etc/kafka/zookeeper.properties")

    def get_bootstrap_server(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return '{}:{}'.format(host, port)

    @wait_container_is_ready(KafkaError, UnrecognizedBrokerVersion, NoBrokersAvailable)
    def _connect(self):
        bootstrap_server = self.get_bootstrap_server()
        consumer = KafkaConsumer(group_id='test', bootstrap_servers=[bootstrap_server])
        if not consumer.topics():
            raise KafkaError("Unable to connect with kafka container!")

    def start(self):
        super().start()
        # Set the environment variables for which we need to know the port mappings and configure
        # kafka.
        exposed_port = self.get_exposed_port(self.port_to_expose)
        host = self.get_container_host_ip()
        advertised_listeners = f'PLAINTEXT://localhost:{exposed_port},BROKER://{host}:9092'
        code, output = self._container.exec_run(
            f'sh -c \'KAFKA_ADVERTISED_LISTENERS="{advertised_listeners}" '
            '/etc/confluent/docker/configure\''
        )
        assert code == 0, output

        # Start Kafka.
        self._container.exec_run('/etc/confluent/docker/launch', detach=True)
        self._connect()
        return self
