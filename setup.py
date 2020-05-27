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

with open('README.rst') as fp:
    long_description = fp.read()

setuptools.setup(
    name='testcontainers',
    packages=setuptools.find_packages(exclude=['tests']),
    version='3.0.2',
    description='Library provides lightweight, throwaway instances of common databases, Selenium '
                'web browsers, or anything else that can run in a Docker container',
    author='Sergey Pirogov',
    author_email='automationremarks@gmail.com',
    url='https://github.com/testcontainers/testcontainers-python',
    keywords=['testing', 'logging', 'docker', 'test automation'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    install_requires=[
        'docker',
        'wrapt',
        'crayons',
        'blindspin',
        'deprecation',
    ],
    extras_require={
        'docker-compose': ['docker-compose'],
        'mysql': ['sqlalchemy', 'pymysql'],
        'oracle': ['sqlalchemy', 'cx_Oracle'],
        'postgresql': ['sqlalchemy', 'psycopg2-binary'],
        'selenium': ['selenium'],
        'google-cloud-pubsub': ['google-cloud-pubsub'],
        'mongo': ['pymongo'],
        'redis': ['redis'],
        'mssqlserver': ['pyodbc']
    },
    long_description_content_type="text/x-rst",
    long_description=long_description,
    python_requires='>=3.5',
)
