from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-postgres",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="PostgreSQL component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "sqlalchemy",
        "psycopg2-binary",
    ],
    python_requires=">=3.7",
)
