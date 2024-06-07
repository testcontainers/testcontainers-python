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

        # reusable client context:
        self.client = None

    @wait_container_is_ready()
    def _connect(self) -> None:
        client, err = self.get_client()
        if err != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Failed to estabilish a connection: {err}")
        if not client.is_connected():
            raise TimeoutError(f"The Paho MQTT secondary thread has not connected yet!")

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
            self.client.loop_start()  # launch a thread to call loop() and dequeue the message

        return self.client, err

    def start(self) -> Self:
        super().start()
        self._connect()
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        self.client.disconnect()
        self.client = None  # force recreation of the client object at next start()
        super().stop(force, delete_volume)

    def publish_message(self, topic: str, payload: str, timeout: int = 2) -> None:
        ret = self.client.publish(topic, payload)
        ret.wait_for_publish(timeout=timeout)
        if not ret.is_published():
            raise RuntimeError(f"Could not publish a message on topic {topic} to Mosquitto broker: {ret}")
