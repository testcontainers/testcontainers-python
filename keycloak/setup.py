from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-keycloak",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="Keycloak component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "python-keycloak",
    ],
    python_requires=">=3.7",
)
