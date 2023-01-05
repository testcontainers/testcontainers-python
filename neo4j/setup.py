from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-neo4j",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="Neo4j component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "neo4j",
    ],
    python_requires=">=3.7",
)
