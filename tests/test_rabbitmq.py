import pytest
from testcontainers.rabbitmq import RabbitmqContainer
import time
import pika

def test_declare_queue():
    rabbitmq_container = RabbitmqContainer("rabbitmq:3-management")
    with rabbitmq_container as rabbit:
        time.sleep(30)
        assert rabbit.declare_queue("prova")[1] == b'queue declared\n'


def test_connection():
    rabbitmq_container = RabbitmqContainer("rabbitmq:3-management")
    with rabbitmq_container as rabbit:
        time.sleep(30)
        a = rabbit.get_connection()
        print(str(a))