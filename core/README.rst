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

.. autoclass:: testcontainers.core.transferable.Transferable

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

Copying a file from disk into a container:

.. doctest::

    >>> import tempfile
    >>> from pathlib import Path
    >>> from testcontainers.core.container import DockerContainer

    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     my_file = Path(tmp) / "my_file.txt"
    ...     _ = my_file.write_text("file content")
    ...     with DockerContainer("bash", command="sleep infinity") as container:
    ...         container.copy_into_container(my_file, "/tmp/my_file.txt")
    ...         result = container.exec("cat /tmp/my_file.txt")
    ...         result.output
    b'file content'
