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

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs

if TYPE_CHECKING:
    from paho.mqtt.client import Client
    from paho.mqtt.enums import MQTTErrorCode


class MosquittoContainer(DockerContainer):
    """
    Specialization of DockerContainer for MQTT broker Mosquitto.
    Example:

        .. doctest::

            >>> from testcontainers.mqtt import MosquittoContainer

            >>> with MosquittoContainer() as mosquitto_broker:
            ...     mqtt_client = mosquitto_broker.get_client()
    """

    TESTCONTAINERS_CLIENT_ID = "TESTCONTAINERS-CLIENT"
    MQTT_PORT = 1883
    CONFIG_FILE = "testcontainers-mosquitto-default-configuration.conf"

    def __init__(
        self,
        image: str = "eclipse-mosquitto:latest",
        # password: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(image, **kwargs)
        # self.password = password
        # reusable client context:
        self.client: Optional["Client"] = None

    @wait_container_is_ready()
    def get_client(self) -> "Client":
        """
        Creates and connects a client, caching the result in `self.client`
        returning that if it exists.

        Connection attempts are retried using `@wait_container_is_ready`.

        Returns:
            a client from the paho library
        """
        if self.client:
            return self.client
        client, err = self.new_client()
        # 0 is a conventional "success" value in C, which is falsy in python
        if err:
            # retry, maybe it is not available yet
            raise ConnectionError(f"Failed to establish a connection: {err}")
        if not client.is_connected():
            raise TimeoutError("The Paho MQTT secondary thread has not connected yet!")
        self.client = client
        return client

    def new_client(self, **kwargs) -> tuple["Client", "MQTTErrorCode"]:
        """
        Get a paho.mqtt client connected to this container.
        Check the returned object is_connected() method before use

        Usage of this method is required for versions <2;
        versions >=2 will wait for log messages to determine container readiness.
        There is no way to pass arguments to new_client in versions <2,
        please use an up-to-date version.

        Args:
            **kwargs: Keyword arguments passed to `paho.mqtt.client`.

        Returns:
            client: MQTT client to connect to the container.
            error: an error code or MQTT_ERR_SUCCESS.
        """
        try:
            from paho.mqtt.client import CallbackAPIVersion, Client
            from paho.mqtt.enums import MQTTErrorCode
        except ImportError as i:
            raise ImportError("'pip install paho-mqtt' required for MosquittoContainer.new_client") from i

        err = MQTTErrorCode.MQTT_ERR_SUCCESS
        if self.client is None:
            self.client = Client(
                client_id=MosquittoContainer.TESTCONTAINERS_CLIENT_ID,
                callback_api_version=CallbackAPIVersion.VERSION2,
                userdata=self,
                **kwargs,
            )
            self.client._connect_timeout = 1.0

            # connect() is a blocking call:
            err = self.client.connect(self.get_container_host_ip(), int(self.get_exposed_port(self.MQTT_PORT)))
            self.client.loop_start()  # launch a thread to call loop() and dequeue the message

        return self.client, err

    def start(self, configfile: Optional[str] = None) -> Self:
        # setup container:
        self.with_exposed_ports(self.MQTT_PORT)
        if configfile is None:
            # default config file
            configfile = Path(__file__).parent / MosquittoContainer.CONFIG_FILE
        self.with_volume_mapping(configfile, "/mosquitto/config/mosquitto.conf")
        # if self.password:
        #     # TODO: add authentication
        #     pass

        # do container start
        super().start()

        self._wait()
        return self

    def _wait(self):
        if self.image.split(":")[-1].startswith("1"):
            import logging

            logging.warning(
                "You are using version 1 of eclipse-mosquitto which is not supported for use by this module without paho-mqtt also installed"
            )
            self.get_client()
        else:
            wait_for_logs(self, r"mosquitto version \d+.\d+.\d+ running", timeout=30)

    def stop(self, force=True, delete_volume=True) -> None:
        if self.client is not None:
            self.client.disconnect()
            self.client = None  # force recreation of the client object at next start()
        super().stop(force, delete_volume)

    def publish_message(self, topic: str, payload: str, timeout: int = 2) -> None:
        ret = self.get_client().publish(topic, payload)
        ret.wait_for_publish(timeout=timeout)
        if not ret.is_published():
            raise RuntimeError(f"Could not publish a message on topic {topic} to Mosquitto broker: {ret}")
