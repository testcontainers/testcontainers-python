import time

import paho.mqtt.client as mqtt

from testcontainers.mqtt import MqttContainer


def basic_example():
    with MqttContainer() as mqtt_container:
        # Get connection parameters
        host = mqtt_container.get_container_host_ip()
        port = mqtt_container.get_exposed_port(mqtt_container.port)

        # Create MQTT client
        client = mqtt.Client()

        # Define callback functions
        def on_connect(client, userdata, flags, rc):
            print(f"Connected with result code {rc}")
            # Subscribe to topics
            client.subscribe("test/topic")

        def on_message(client, userdata, msg):
            print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

        # Set callbacks
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to broker
        client.connect(host, port)
        client.loop_start()

        # Publish test messages
        test_messages = ["Hello MQTT!", "This is a test message", "MQTT is working!"]

        for msg in test_messages:
            client.publish("test/topic", msg)
            print(f"Published message: {msg}")
            time.sleep(1)  # Wait a bit between messages

        # Wait for messages to be processed
        time.sleep(2)

        # Clean up
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    basic_example()
