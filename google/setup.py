from setuptools import setup, find_namespace_packages

setup(
    name="testcontainers-gcp",
    version="0.0.1rc1",
    packages=find_namespace_packages(),
    description="Google Cloud Platform component of testcontainers-python.",
    url="https://github.com/testcontainers/testcontainers-python",
    install_requires=[
        "testcontainers-core",
        "google-cloud-pubsub < 2",
    ],
    python_requires=">=3.7",
)
