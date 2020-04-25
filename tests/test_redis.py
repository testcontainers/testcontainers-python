import time

from testcontainers.redis import RedisContainer


def test_docker_run_redis():
    config = RedisContainer()
    with config as redis:
        client = redis.get_client()
        p = client.pubsub()
        p.subscribe('test')
        client.publish('test', 'new_msg')
        msg = wait_for_message(p)
        assert 'data' in msg
        assert b'new_msg', msg['data']


def wait_for_message(pubsub, timeout=1, ignore_subscribe_messages=True):
    now = time.time()
    timeout = now + timeout
    while now < timeout:
        message = pubsub.get_message(
            ignore_subscribe_messages=ignore_subscribe_messages)
        if message is not None:
            return message
        time.sleep(0.01)
        now = time.time()
    return None
