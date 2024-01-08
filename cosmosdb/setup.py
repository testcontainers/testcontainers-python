from setuptools import setup, find_namespace_packages

description = "CosmoDB component of testcontainers-python."

setup(
    name="testcontainers-cosmosdb",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description=description,
    long_description=description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jbt-omniblu/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "azure-cosmos",
        "azure.core"
    ],
    python_requires=">=3.7",
)
