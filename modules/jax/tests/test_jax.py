import pytest
from testcontainers.jax import JAXContainer

def test_jax_container():
    with JAXContainer() as jax_container:
        jax_container.connect()
        
        # Test running a simple JAX computation
        result = jax_container.run_jax_command("import jax; print(jax.numpy.add(1, 1))")
        assert "2" in result.output.decode()

def test_jax_container_gpu_support():
    with JAXContainer() as jax_container:
        jax_container.connect()
        
        # Test GPU availability
        result = jax_container.run_jax_command(
            "import jax; print(jax.devices())"
        )
        assert "gpu" in result.output.decode().lower()

def test_jax_container_jupyter():
    with JAXContainer() as jax_container:
        jax_container.connect()
        
        jupyter_url = jax_container.get_jupyter_url()
        assert jupyter_url.startswith("http://")
        assert ":8888" in jupyter_url