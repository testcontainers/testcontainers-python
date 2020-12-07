import time

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.rabbitmq import RabbitmqContainer

def test_declare_queue():
    rabbitmq_container = RabbitmqContainer("rabbitmq:3-management")
    queue_name = "test"
    with rabbitmq_container as rabbit:
        wait_for_logs(rabbit, RabbitmqContainer.SERVICE_STARTED, timeout=30, interval=1)
        time.sleep(30)
        assert rabbit.declare_queue(queue_name)[1] == b'queue declared\n'


def test_connection():
    rabbitmq_container = RabbitmqContainer("rabbitmq:3-management")
    with rabbitmq_container as rabbit:
        wait_for_logs(rabbit, RabbitmqContainer.SERVICE_STARTED, timeout=30, interval=1)
        _, exposed_port = rabbit.get_connection()
        assert exposed_port == 5672

