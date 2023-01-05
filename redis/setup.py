from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-redis",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="Redis component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "redis",
    ],
    python_requires=">=3.7",
)
