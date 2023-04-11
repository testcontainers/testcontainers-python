from setuptools import setup, find_namespace_packages

description = "Azurite component of testcontainers-python."

setup(
    name="testcontainers-azurite",
    version="0.1.0",
    packages=find_namespace_packages(),
    description=description,
    long_description=description,
    long_description_content_type="text/x-rst",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "azure-storage-blob",
    ],
    python_requires=">=3.7",
)
