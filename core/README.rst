testcontainers-core
===================

:code:`testcontainers-core` is the core functionality for spinning up Docker containers in test environments.

.. autoclass:: testcontainers.core.container.DockerContainer

.. autoclass:: testcontainers.core.image.DockerImage

Using `DockerContainer` and `DockerImage` directly:

.. doctest::

    >>> from testcontainers.core.container import DockerContainer
    >>> from testcontainers.core.waiting_utils import wait_for_logs
    >>> from testcontainers.core.image import DockerImage

    >>> with DockerImage(path="./core/tests/image_fixtures/sample/", tag="test-sample:latest") as image:
    ...     with DockerContainer(str(image)) as container:
    ...         delay = wait_for_logs(container, "Test Sample Image")
