from setuptools import setup, find_namespace_packages

description = "Core component of testcontainers-python."

setup(
    name="testcontainers-core",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description=description,
    long_description=description,
    long_description_content_type="text/x-rst",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "docker>=4.0.0",
        "urllib3<2.0",  # https://github.com/docker/docker-py/issues/3113#issuecomment-1533389349
        "wrapt",
    ],
    python_requires=">=3.7",
)
