from testcontainers.core.generic import DockerContainer


def test_container_port():
    cont = DockerContainer("selenium/hub", "latest", "selenium_hub")
    cont.start()

    assert cont.get_host_info(4444) > 0