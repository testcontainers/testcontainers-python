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
from unittest.mock import patch

from google.cloud import pubsub
from testcontainers.core.container import DockerContainer


class PubSubContainer(DockerContainer):
    """
    PubSub container for testing managed message queues.

    Example:

        The example will spin up a Google Cloud PubSub emulator that you can use for integration
        tests. The :code:`pubsub` instance provides convenience methods :code:`get_publisher` and
        :code:`get_subscriber` to connect to the emulator without having to set the environment
        variable :code:`PUBSUB_EMULATOR_HOST`.

        .. doctest::

            >>> from testcontainers.google import PubSubContainer

            >>> config = PubSubContainer()
            >>> with config as pubsub:
            ...    publisher = pubsub.get_publisher_client()
            ...    topic_path = publisher.topic_path(pubsub.project, "my-topic")
            ...    topic = publisher.create_topic(name=topic_path)
    """

    def __init__(
        self, image: str = "google/cloud-sdk:emulators", project: str = "test-project", port: int = 8432, **kwargs
    ) -> None:
        super().__init__(image=image, **kwargs)
        self.project = project
        self.port = port
        self.with_exposed_ports(self.port)
        self.with_command(f"gcloud beta emulators pubsub start --project={project} --host-port=0.0.0.0:{port}")

    def get_pubsub_emulator_host(self) -> str:
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"

    def _get_client(self, cls: type, **kwargs) -> dict:
        with patch.dict(os.environ, PUBSUB_EMULATOR_HOST=self.get_pubsub_emulator_host()):
            return cls(**kwargs)

    def get_publisher_client(self, **kwargs) -> pubsub.PublisherClient:
        from google.auth import credentials

        kwargs["client_options"] = {"api_endpoint": self.get_pubsub_emulator_host()}
        kwargs["credentials"] = credentials.AnonymousCredentials()
        return self._get_client(pubsub.PublisherClient, **kwargs)

    def get_subscriber_client(self, **kwargs) -> pubsub.SubscriberClient:
        from google.auth import credentials

        kwargs["client_options"] = {"api_endpoint": self.get_pubsub_emulator_host()}
        kwargs["credentials"] = credentials.AnonymousCredentials()
        return self._get_client(pubsub.SubscriberClient, **kwargs)
