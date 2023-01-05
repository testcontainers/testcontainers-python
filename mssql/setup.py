from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-mssql",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="Microsoft SQL Server component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "pymssql",
    ],
    python_requires=">=3.7",
)
