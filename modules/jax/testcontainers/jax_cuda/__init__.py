import logging
from urllib.error import URLError

from core.testcontainers.core.container import DockerContainer
from core.testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs


class JAXContainer(DockerContainer):
    """
    JAX container for GPU-accelerated numerical computing and machine learning.

    Example:

    .. doctest::

        >>> from testcontainers.jax import JAXContainer

        >>> with JAXContainer("nvcr.io/nvidia/jax:23.08-py3") as jax_container:
        ...     # Connect to the container
        ...     jax_container.connect()
        ...
        ...     # Run a simple JAX computation
        ...     result = jax_container.run_jax_command("import jax; print(jax.numpy.add(1, 1))")
        ...     assert "2" in result.output

    .. auto-class:: JAXContainer
        :members:
        :undoc-members:
        :show-inheritance:
    """

    def __init__(self, image="nvcr.io/nvidia/jax:23.08-py3", **kwargs):
        super().__init__(image, **kwargs)
        self.with_env("NVIDIA_VISIBLE_DEVICES", "all")
        self.with_env("CUDA_VISIBLE_DEVICES", "all")
        self.with_kwargs(runtime="nvidia")  # Use NVIDIA runtime for GPU support
        self.start_timeout = 600  # 10 minutes
        self.connection_retries = 5
        self.connection_retry_delay = 10  # seconds

    @wait_container_is_ready(URLError)
    def _connect(self):
        # Check if JAX is properly installed and functioning
        result = self.run_jax_command(
            "import jax; import jaxlib; "
            "print(f'JAX version: {jax.__version__}'); "
            "print(f'JAXlib version: {jaxlib.__version__}'); "
            "print(f'Available devices: {jax.devices()}'); "
            "print(jax.numpy.add(1, 1))"
        )

        if "JAX version" in result.output and "Available devices" in result.output:
            logging.info(f"JAX environment verified:\n{result.output}")
        else:
            raise Exception("JAX environment check failed")

    def connect(self):
        """
        Connect to the JAX container and ensure it's ready.
        This method verifies that JAX is properly installed and functioning.
        It also checks for available devices, including GPUs if applicable.
        """
        self._connect()
        logging.info("Successfully connected to JAX container and verified the environment")

    def run_jax_command(self, command):
        """
        Run a JAX command inside the container.
        """
        exec_result = self.exec(f"python -c '{command}'")
        return exec_result

    def _wait_for_container_to_be_ready(self):
        wait_for_logs(self, "JAX is ready", timeout=self.start_timeout)

    def start(self):
        """
        Start the JAX container and wait for it to be ready.
        """
        super().start()
        self._wait_for_container_to_be_ready()
        logging.info("JAX container started and ready.")
        return self

    def stop(self, force=True, delete_volume=True) -> None:
        """
        Stop the JAX container.
        """
        super().stop(force, delete_volume)
        logging.info("JAX container stopped.")

    @property
    def timeout(self):
        """
        Get the container start timeout.
        """
        return self.start_timeout
