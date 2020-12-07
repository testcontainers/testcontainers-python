import time

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.rabbitmq import RabbitmqContainer

def test_declare_queue():
    rabbitmq_container = RabbitmqContainer("rabbitmq:3-management")
    with rabbitmq_container as rabbit:
        wait_for_logs(rabbit, r"Server startup complete;", timeout=30, interval=1)
        time.sleep(30)
        _, a = rabbit.declare_queue("prova")
        assert a == b'queue declared\n'


def test_connection():
    rabbitmq_container = RabbitmqContainer("rabbitmq:3-management")
    with rabbitmq_container as rabbit:
        wait_for_logs(rabbit, r"Server startup complete;", timeout=30, interval=1)
        a = rabbit.get_connection()
        print(str(a))