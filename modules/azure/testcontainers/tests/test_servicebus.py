import logging
from typing import cast

from _pytest.logging import LogCaptureFixture
from azure.servicebus import ServiceBusClient, ServiceBusMessage

from testcontainers.core.network import Network
from testcontainers.azure import ServiceBusContainer
from testcontainers.mssql import SqlServerContainer

from ._types import ServiceBusConfiguration

log = logging.getLogger(__name__)

# Default namespace.
NAMESPACE = "sbemulatorns"
TOPIC = "demo-topic"
SUBSCRIPTION = "demo-subscription"

CONFIG = {
    "UserConfig": {
        "Namespaces": [
            {
                "Name": NAMESPACE,
                "Queues": [],
                "Topics": [
                    {
                        "Name": TOPIC,
                        "Properties": {
                            "DefaultMessageTimeToLive": "PT1H",
                            "DuplicateDetectionHistoryTimeWindow": "PT20S",
                            "RequiresDuplicateDetection": False,
                        },
                        "Subscriptions": [
                            {
                                "Name": SUBSCRIPTION,
                                "Properties": {
                                    "DeadLetteringOnMessageExpiration": False,
                                    "DefaultMessageTimeToLive": "PT1H",
                                    "LockDuration": "PT1M",
                                    "MaxDeliveryCount": 10,
                                    "ForwardDeadLetteredMessagesTo": "",
                                    "ForwardTo": "",
                                    "RequiresSession": False,
                                },
                                "Rules": [],
                            },
                        ],
                    }
                ],
            }
        ],
        "Logging": {"Type": "File"},
    }
}


def test_service_bus_integration(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)

    network = Network().create()

    mssql_container = SqlServerContainer(
        "mcr.microsoft.com/mssql/server:2022-CU12-ubuntu-22.04", password="d0gs>cats!!!"
    )
    mssql_container.with_env("ACCEPT_EULA", "Y")
    mssql_container.with_network(network)
    mssql_container.with_exposed_ports(1433)

    with ServiceBusContainer(
        config=cast(ServiceBusConfiguration, CONFIG), network=network, mssql_container=mssql_container
    ).accept_license() as sbemulator:
        conn_str = sbemulator.get_connection_url()
        log.debug("Using %r as endpoint", conn_str)

        test_message = "potato"

        client = ServiceBusClient.from_connection_string(conn_str, logging_enable=True)
        with client.get_topic_sender(topic_name=TOPIC) as sender:
            sender.send_messages(ServiceBusMessage(test_message))

        handler_client = ServiceBusClient.from_connection_string(conn_str, logging_enable=True)

        with handler_client.get_subscription_receiver(subscription_name=SUBSCRIPTION, topic_name=TOPIC) as receiver:
            received = receiver.receive_messages(max_message_count=1, max_wait_time=5)
            message = next(received[0].body).decode()
            assert message == test_message
