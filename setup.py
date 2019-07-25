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

with open('README.md') as fp:
    long_description = fp.read()

setuptools.setup(
    name='testcontainers',
    packages=setuptools.find_packages(exclude=['tests']),
    version='2.5',
    description=('Library provides lightweight, throwaway '
                 'instances of common databases, '
                 'Selenium web browsers, or anything else that can '
                 'run in a Docker container'),
    author='Sergey Pirogov',
    author_email='automationremarks@gmail.com',
    url='https://github.com/testcontainers/testcontainers-python',
    keywords=['testing', 'logging', 'docker', 'test automation'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: '
        'Libraries :: Python Modules',
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
    ],
    extras_require={
        'docker-compose': ['docker-compose'],
        'mysql': ['sqlalchemy', 'pymysql'],
        'postgresql': ['sqlalchemy', 'psycopg2'],
        'selenium': ['selenium==2.53.1'],
        'google-cloud-pubsub': ['google-cloud-pubsub'],
    },
    long_description_content_type="text/markdown",
    long_description=long_description,
)
