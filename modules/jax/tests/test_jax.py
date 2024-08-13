import pytest
from modules.jax.testcontainers.jax_cuda import JAXContainer


@pytest.fixture(scope="module")
def jax_container():
    with JAXContainer() as container:
        container.connect()
        yield container


def test_jax_container_basic_computation(jax_container):
    result = jax_container.run_jax_command("import jax; print(jax.numpy.add(1, 1))")
    assert "2" in result.output.decode(), "Basic JAX computation failed"


def test_jax_container_version(jax_container):
    result = jax_container.run_jax_command("import jax; print(jax.__version__)")
    assert result.exit_code == 0, "Failed to get JAX version"
    assert result.output.decode().strip(), "JAX version is empty"


def test_jax_container_gpu_support(jax_container):
    result = jax_container.run_jax_command(
        "import jax; devices = jax.devices(); " "print(any(dev.platform == 'gpu' for dev in devices))"
    )
    assert "True" in result.output.decode(), "No GPU device found"


def test_jax_container_matrix_multiplication(jax_container):
    command = """
import jax
import jax.numpy as jnp
x = jnp.array([[1, 2], [3, 4]])
y = jnp.array([[5, 6], [7, 8]])
result = jnp.dot(x, y)
print(result)
    """
    result = jax_container.run_jax_command(command)
    assert "[[19 22]\n [43 50]]" in result.output.decode(), "Matrix multiplication failed"


def test_jax_container_custom_image():
    custom_image = "nvcr.io/nvidia/jax:23.09-py3"
    with JAXContainer(image=custom_image) as container:
        container.connect()
        result = container.run_jax_command("import jax; print(jax.__version__)")
        assert result.exit_code == 0, f"Failed to run JAX with custom image {custom_image}"
