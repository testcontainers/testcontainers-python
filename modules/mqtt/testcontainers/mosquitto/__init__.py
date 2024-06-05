#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import time
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
from typing_extensions import Self

from paho.mqtt import client as mqtt_client
import paho.mqtt.enums
from queue import Queue
from typing import Optional

# MosquittoContainer


class MosquittoContainer(DockerContainer):
    """
    Specialization of DockerContainer for MQTT broker Mosquitto.
    Example:

        .. doctest::

            >>> from testcontainers.mosquitto import MosquittoContainer

            >>> with MosquittoContainer() as mosquitto_broker:
            ...     mqtt_client = mosquitto_broker.get_client()
    """

    TESTCONTAINER_CLIENT_ID = "TESTCONTAINER-CLIENT"
    DEFAULT_PORT = 1883
    CONFIG_FILE = "integration-test-mosquitto.conf"

    def __init__(
        self,
        image: str = "eclipse-mosquitto:latest",
        port: int = None,
        configfile: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> None:
        # raise_for_deprecated_parameter(kwargs, "port_to_expose", "port")
        super().__init__(image, **kwargs)

        if port is None:
            self.port = MosquittoContainer.DEFAULT_PORT
        else:
            self.port = port
        self.password = password

        # setup container:
        self.with_exposed_ports(self.port)
        if configfile is None:
            # default config ifle
            TEST_DIR = os.path.dirname(os.path.abspath(__file__))
            configfile = os.path.join(TEST_DIR, MosquittoContainer.CONFIG_FILE)
        self.with_volume_mapping(configfile, "/mosquitto/config/mosquitto.conf")
        if self.password:
            # TODO: add authentication
            pass

        # helper used to turn asynchronous methods into synchronous:
        self.msg_queue = Queue()

        # dictionary of watched topics and their message counts:
        self.watched_topics = {}

        # reusable client context:
        self.client = None

    @wait_container_is_ready()
    def _connect(self) -> None:
        client, err = self.get_client()
        if err != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Failed to estabilish a connection: {err}")

        interval = 1.0
        timeout = 5
        start = time.time()
        while True:
            duration = time.time() - start
            if client.is_connected():
                return
            if duration > timeout:
                raise TimeoutError(f"Failed to estabilish a connection after {timeout:.3f} " "seconds")
            # wait till secondary thread manages to connect successfully:
            time.sleep(interval)

    def get_client(self, **kwargs) -> tuple[mqtt_client.Client, paho.mqtt.enums.MQTTErrorCode]:
        """
        Get a paho.mqtt client connected to this container.
        Check the returned object is_connected() method before use

        Args:
            **kwargs: Keyword arguments passed to `paho.mqtt.client`.

        Returns:
            client: MQTT client to connect to the container.
            error: an error code or MQTT_ERR_SUCCESS.
        """
        err = paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS
        if self.client is None:
            self.client = mqtt_client.Client(
                client_id=MosquittoContainer.TESTCONTAINER_CLIENT_ID,
                callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
                userdata=self,
                **kwargs,
            )
            self.client._connect_timeout = 1.0

            # connect() is a blocking call:
            err = self.client.connect(self.get_container_host_ip(), int(self.get_exposed_port(self.port)))
            self.client.on_message = MosquittoContainer.on_message
            self.client.loop_start()  # launch a thread to call loop() and dequeue the message

        return self.client, err

    def start(self) -> Self:
        super().start()
        self._connect()
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        self.client.disconnect()
        self.client = None  # force recreation of the client object at next start()
        self.watched_topics = {}  # clean all watched topics as well
        super().stop(force, delete_volume)

    class WatchedTopicInfo:
        def __init__(self):
            self.count = 0
            self.timestamp_start_watch = time.time()
            self.last_payload = ""

        def on_message(self, msg: mqtt_client.MQTTMessage):
            self.count += 1
            # for simplicity: assume strings are used in integration tests and are UTF8-encoded:
            self.last_payload = msg.payload.decode("UTF-8")

        def get_count(self):
            return self.count

        def get_last_payload(self):
            return self.last_payload

        def get_rate(self):
            duration = time.time() - self.timestamp_start_watch
            if duration > 0:
                return self.count / duration
            return 0

    def on_message(client: mqtt_client.Client, mosquitto_container: "MosquittoContainer", msg: mqtt_client.MQTTMessage):
        # very verbose but useful for debug:
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == "$SYS/broker/messages/received":
            mosquitto_container.msg_queue.put(msg)
        else:
            # this should be a topic added through the watch_topics() API...
            # just check it has not been removed (e.g. by unwatch_all):
            if msg.topic in mosquitto_container.watched_topics:
                mosquitto_container.watched_topics[msg.topic].on_message(msg)
            else:
                print(f"Received msg on topic [{msg.topic}] that is not being watched")

    def get_messages_received(self) -> int:
        """
        Returns the total number of messages received by the broker so far.
        """

        client, err = self.get_client()
        if not client.is_connected():
            raise RuntimeError(f"Could not connect to Mosquitto broker: {err}")

        client.subscribe("$SYS/broker/messages/received")

        # wait till we get the first message from the topic;
        # this wait will be up to 'sys_interval' second long (see mosquitto.conf)
        try:
            message = self.msg_queue.get(block=True, timeout=5)
            return int(message.payload.decode())
        except Queue.Empty:
            return 0

    def watch_topics(self, topics: list):
        client, err = self.get_client()
        if not client.is_connected():
            raise RuntimeError(f"Could not connect to Mosquitto broker: {err}")

        filtered_topics = []
        for t in topics:
            if t in self.watched_topics:
                continue  # nothing to do... the topic had already been subscribed
            self.watched_topics[t] = MosquittoContainer.WatchedTopicInfo()
            # the topic list is actually a list of tuples (topic_name,qos)
            filtered_topics.append((t, 0))

        # after subscribe() the on_message() callback will be invoked
        err, _ = client.subscribe(filtered_topics)
        if err != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Failed to subscribe to topics: {filtered_topics}")

    def unwatch_all(self):
        client, err = self.get_client()
        if not client.is_connected():
            raise RuntimeError(f"Could not connect to Mosquitto broker: {err}")

        # unsubscribe from all topics
        client.unsubscribe(list(self.watched_topics.keys()))
        self.watched_topics = {}

    def get_messages_received_in_watched_topic(self, topic: str) -> int:
        if topic not in self.watched_topics:
            raise RuntimeError(f"Topic {topic} is not watched! Fix the test")
        return self.watched_topics[topic].get_count()

    def get_last_payload_received_in_watched_topic(self, topic: str) -> int:
        if topic not in self.watched_topics:
            raise RuntimeError(f"Topic {topic} is not watched! Fix the test")
        return self.watched_topics[topic].get_last_payload()

    def get_message_rate_in_watched_topic(self, topic: str) -> int:
        if topic not in self.watched_topics:
            raise RuntimeError(f"Topic {topic} is not watched! Fix the test")
        return self.watched_topics[topic].get_rate()

    def publish_message(self, topic: str, payload: str):
        ret = self.client.publish(topic, payload)
        ret.wait_for_publish(timeout=2)
        if not ret.is_published():
            raise RuntimeError(f"Could not publish a message on topic {topic} to Mosquitto broker: {ret}")

    def print_logs(self) -> str:
        print("** BROKER LOGS [STDOUT]:")
        print(self.get_logs()[0].decode())
        print("** BROKER LOGS [STDERR]:")
        print(self.get_logs()[1].decode())
