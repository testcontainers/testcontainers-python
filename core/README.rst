Testcontainers Core
===================

:code:`testcontainers-core` is the core functionality for spinning up Docker containers in test environments.

.. autoclass:: testcontainers.core.container.DockerContainer
    :members: with_bind_ports, with_exposed_ports

.. note::
    When using `with_bind_ports` or `with_exposed_ports`
    you can specify the port in the following formats: :code:`{private_port}/{protocol}`

    e.g. `8080/tcp` or `8125/udp` or just `8080` (default protocol is tcp)

    For legacy reasons, the port can be an *integer*

.. autoclass:: testcontainers.core.image.DockerImage

.. autoclass:: testcontainers.core.generic.DbContainer

.. autoclass:: testcontainers.core.network.Network

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
