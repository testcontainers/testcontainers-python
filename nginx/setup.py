from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-nginx",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="NGINX component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
    ],
    python_requires=">=3.7",
)
