Testcontainers Core
===================

:code:`testcontainers-core` is the core functionality for spinning up Docker containers in test environments.

.. automodule:: testcontainers.core.container
    :members:
    :undoc-members:

.. autoclass:: testcontainers.core.network.Network
    :members:

.. autoclass:: testcontainers.core.image.DockerImage

.. autoclass:: testcontainers.core.generic.DbContainer

.. autoclass:: testcontainers.core.wait_strategies.WaitStrategy

.. raw:: html

    <hr>

Compose
-------

It is also possible to use Docker Compose functionality:

.. automodule:: testcontainers.compose.compose
    :members:

.. raw:: html

    <hr>

Examples
--------

Using `DockerContainer` and `DockerImage` to create a container:

.. doctest::

    >>> from testcontainers.core.container import DockerContainer
    >>> from testcontainers.core.waiting_utils import wait_for_logs
    >>> from testcontainers.core.image import DockerImage

    >>> with DockerImage(path="./core/tests/image_fixtures/sample/", tag="test-sample:latest") as image:
    ...     with DockerContainer(str(image)) as container:
    ...         delay = wait_for_logs(container, "Test Sample Image")

The `DockerImage` class is used to build the image from the specified path and tag.
The `DockerContainer` class is then used to create a container from the image.


Creating a container with an exposed port and a custom environment variable:

.. doctest::

    >>> from testcontainers.core.container import DockerContainer
    >>> from testcontainers.core.waiting_utils import wait_for_logs

    >>> container = DockerContainer("stain/jena-fuseki:latest")
    >>> container.with_exposed_ports(3030)
    >>> container.with_env("ADMIN_PASSWORD", "password")
    >>> container.start()
    >>> delay = wait_for_logs(container, "Fuseki is available")
    >>> container_url = f"http://{container.get_container_host_ip()}:{container.get_exposed_port(3030)}"
