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

from ..core.container import DockerContainer


class PubSubContainer(DockerContainer):
    """
    PubSub container for testing managed message queues.

    Example
    -------
    The example will spin up a Google Cloud PubSub emulator that you can use for integration tests.
    The :code:`pubsub` instance provides convenience methods :code:`get_publisher` and
    :code:`get_subscriber` to connect to the emulator without having to set the environment variable
    :code:`PUBSUB_EMULATOR_HOST`.
    ::

        def test_docker_run_pubsub():
            config = PubSubContainer('google/cloud-sdk:latest')
            with config as pubsub:
                publisher = pubsub.get_publisher()
                topic_path = publisher.topic_path(pubsub.project, "my-topic")
                topic = publisher.create_topic(topic_path)
    """
    def __init__(self, image="google/cloud-sdk:latest",
                 project="test-project", port=8432):
        super(PubSubContainer, self).__init__(image=image)
        self.project = project
        self.port = port
        self.with_exposed_ports(self.port)
        self.with_command("gcloud beta emulators pubsub start --project="
                          "{project} --host-port=0.0.0.0:{port}".format(
                              project=self.project, port=self.port,
                          ))

    def get_pubsub_emulator_host(self):
        return "{host}:{port}".format(host=self.get_container_host_ip(),
                                      port=self.get_exposed_port(self.port))

    def _get_channel(self, channel=None):
        if channel is None:
            import grpc
            return grpc.insecure_channel(target=self.get_pubsub_emulator_host())

    def get_publisher_client(self, **kwargs):
        from google.cloud import pubsub
        kwargs['channel'] = self._get_channel(kwargs.get('channel'))
        return pubsub.PublisherClient(**kwargs)

    def get_subscriber_client(self, **kwargs):
        from google.cloud import pubsub
        kwargs['channel'] = self._get_channel(kwargs.get('channel'))
        return pubsub.SubscriberClient(**kwargs)
