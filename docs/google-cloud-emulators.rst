Google Cloud Emulators
======================

Allows to spin up google cloud emulators, such as PubSub.

PubSub example
--------------

::

    def test_docker_run_pubsub():
        config = PubSubContainer('google/cloud-sdk:latest')
        with config as pubsub:
            publisher = pubsub.get_publisher()
            topic_path = publisher.topic_path(pubsub.project, "my-topic")
            topic = publisher.create_topic(topic_path)

The example will spin up a Google Cloud PubSub emulator that you can use for integration tests. The :code:`pubsub` instance provides convenience methods :code:`get_publisher` and :code:`get_subscriber` to connect to the emulator without having to set the environment variable :code:`PUBSUB_EMULATOR_HOST`.
