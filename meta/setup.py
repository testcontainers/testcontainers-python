#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import setuptools

description = "Python interface for throwaway instances of anything that can run in a Docker " \
    "container."
long_description = f"{description} See https://testcontainers-python.readthedocs.io/en/latest/ " \
    "for details."

setuptools.setup(
    name="testcontainers",
    version="4.0.0rc1",
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Sergey Pirogov",
    author_email="automationremarks@gmail.com",
    url="https://github.com/testcontainers/testcontainers-python",
    keywords=["testing", "logging", "docker", "test automation"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
    install_requires=[
        "testcontainers-core",
    ],
    extras_require={
        "arangodb": ["testcontainers-arangodb"],
        "azurite": ["testcontainers-azurite"],
        "clickhouse": ["testcontainers-clickhouse"],
        "docker-compose": ["testcontainers-compose"],
        "google-cloud-pubsub": ["testcontainers-gcp"],
        "kafka": ["testcontainers-kafka"],
        "keycloak": ["testcontainers-keycloak"],
        "minio": ["testcontainers-minio"],
        "mongo": ["testcontainers-mongo"],
        "mssqlserver": ["testcontainers-mssql"],
        "mysql": ["testcontainers-mysql"],
        "neo4j": ["testcontainers-neo4j"],
        "opensearch": ["testcontainers-opensearch"],
        "oracle": ["testcontainers-oracle"],
        "postgresql": ["testcontainers-postgres"],
        "rabbitmq": ["testcontainers-rabbitmq"],
        "redis": ["testcontainers-redis"],
        "selenium": ["testcontainers-selenium"],
    },
    python_requires=">=3.7",
)
