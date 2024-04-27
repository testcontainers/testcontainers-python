testcontainers-core
===================

:code:`testcontainers-core` is the core functionality for spinning up Docker containers in test environments.

.. autoclass:: testcontainers.core.container.DockerContainer

.. autoclass:: testcontainers.core.image.DockerImage

Conjoint usage:

.. doctest::
    >>> from testcontainers.core.container import DockerContainer
    >>> from testcontainers.core.waiting_utils import wait_for_logs
    >>> from testcontainers.core.image import DockerImage

    >>> with DockerImage(tag="test-image:latest", path=".") as image:
    ...     with DockerContainer(tag=image.tag) as container:
    ...         delay = wait_for_log(container, "Server ready", 60)
