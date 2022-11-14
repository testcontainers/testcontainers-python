import time

from testcontainers.dragonfly import DragonflyContainer

'''
Ensure that Dragonfly is working by publishing messages
And reading them from the subscriber side
'''


def test_docker_run_dragonfly():
    config = DragonflyContainer()
    with config as dragonfly:
        client = dragonfly.get_client()
        p = client.pubsub()
        # Make sure that we are ready to get the messages
        time.sleep(0.01)
        # Make sure that the subscriber started
        p.subscribe('test')
        time.sleep(0.01)
        client.publish('test', 'new_msg')
        msg = wait_for_message(pubsub=p, timeout=10)
        assert msg is not None
        assert 'data' in msg
        assert b'new_msg', msg['data']


'''
Connect to Dragonfly with password and set value, then ensure that the value
was successfully read
'''


def test_docker_run_dragonfly_with_password():
    config = DragonflyContainer(password="mypass")
    with config as dragonfly:
        client = dragonfly.get_client(decode_responses=True)
        client.set("hello", "world")
        assert client.get("hello") == "world"


def wait_for_message(pubsub, timeout=1, ignore_subscribe_messages=True):
    now = time.time()
    timeout = now + timeout
    while now < timeout:
        message = pubsub.get_message(
            ignore_subscribe_messages=ignore_subscribe_messages)
        if message is not None:
            return message
        time.sleep(0.04)
        now = time.time()
    return None
