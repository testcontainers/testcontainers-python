from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-arangodb",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="Arango DB component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "python-arango",
    ],
    python_requires=">=3.7",
)
