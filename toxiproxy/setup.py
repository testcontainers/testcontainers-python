from setuptools import setup, find_namespace_packages

description = "ToxiProxy component of testcontainers-python."

setup(
    name="testcontainers-toxiproxy",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description=description,
    long_description=description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jbt-omniblu/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "toxiproxy @ git+https://github.com/jbt-omniblu/toxiproxy-python.git@update#egg=toxiproxy"
    ],
    python_requires=">=3.7",
)
