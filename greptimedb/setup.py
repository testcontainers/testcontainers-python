from setuptools import find_namespace_packages, setup

description = "GreptimeDB component of testcontainers-python."

setup(
    name="testcontainers-greptimedb",
    version="0.0.1",
    packages=find_namespace_packages(),
    description=description,
    long_description=description,
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=["testcontainers-core", "sqlalchemy", "pymysql[rsa]"],
    python_requires=">=3.7",
)
