from testcontainers.rabbitmq import RabbitmqContainer


def test_docker_run_rabbitmq():
    with RabbitmqContainer() as container:
        connection = container.get_connection()

        channel = connection.channel()

        qname, msg = 'test-queue', 'hello world'

        channel.queue_declare(qname)
        channel.basic_publish(exchange='', routing_key=qname, body=msg)

        _method, _props, payload = channel.basic_get(qname)
        assert payload.decode() == msg
