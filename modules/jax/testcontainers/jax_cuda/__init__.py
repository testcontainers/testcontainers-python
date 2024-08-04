import logging
import urllib.request
from urllib.error import URLError

from core.testcontainers.core.container import DockerContainer
from core.testcontainers.core.waiting_utils import wait_container_is_ready
from core.testcontainers.core.config import testcontainers_config
from core.testcontainers.core.waiting_utils import wait_for_logs

class JAXContainer(DockerContainer):
    """
    JAX container for GPU-accelerated numerical computing and machine learning.

    Example:

    .. doctest::

        >>> import jax
        >>> from testcontainers.jax import JAXContainer

        >>> with JAXContainer("nvcr.io/nvidia/jax:23.08-py3") as jax_container:
        ...     # Connect to the container
        ...     jax_container.connect()
        ...     
        ...     # Run a simple JAX computation
        ...     result = jax.numpy.add(1, 1)
        ...     assert result == 2

    .. auto-class:: JAXContainer
        :members:
        :undoc-members:
        :show-inheritance:
    """

    def __init__(self, image="nvcr.io/nvidia/jax:23.08-py3", **kwargs):
        super().__init__(image, **kwargs)
        self.with_exposed_ports(8888)  # Expose Jupyter notebook port
        self.with_env("NVIDIA_VISIBLE_DEVICES", "all")
        self.with_env("CUDA_VISIBLE_DEVICES", "all")
        self.with_kwargs(runtime="nvidia")  # Use NVIDIA runtime for GPU support
        self.start_timeout = 600 # 10 minutes

    @wait_container_is_ready(URLError)
    def _connect(self):
        url = f"http://{self.get_container_host_ip()}:{self.get_exposed_port(8888)}"
        res = urllib.request.urlopen(url, timeout=self.start_timeout)
        if res.status != 200:
            raise Exception(f"Failed to connect to JAX container. Status: {res.status}")

    def connect(self):
        """
        Connect to the JAX container and ensure it's ready.
        """
        self._connect()
        logging.info("Successfully connected to JAX container")

    def get_jupyter_url(self):
        """
        Get the URL for accessing the Jupyter notebook server.
        """
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(8888)}"

    def run_jax_command(self, command):
        """
        Run a JAX command inside the container.
        """
        exec_result = self.exec(f"python -c '{command}'")
        return exec_result

    def _wait_for_container_to_be_ready(self):
        wait_for_logs(self, "Jupyter Server", timeout=self.start_timeout)

    def start(self):
        """
        Start the JAX container and wait for it to be ready.
        """
        super().start()
        self._wait_for_container_to_be_ready()
        logging.info(f"JAX container started. Jupyter URL: {self.get_jupyter_url()}")
        return self
    
    def stop(self, force=True):
        """
        Stop the JAX container.
        """
        super().stop(force)
        logging.info("JAX container stopped.")

    @property
    def timeout(self):
        """
        Get the container start timeout.
        """
        return self.start_timeout