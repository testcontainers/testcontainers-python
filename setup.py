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

setuptools.setup(
    name='testcontainers',
    packages=setuptools.find_packages(exclude=['tests']),
    version='2.1.0',
    description=('Library provides lightweight, throwaway '
                 'instances of common databases, '
                 'Selenium web browsers, or anything else that can '
                 'run in a Docker containers'),
    author='Sergey Pirogov',
    author_email='automationremarks@gmail.com',
    url='https://github.com/SergeyPirogov/python-testcontainers',
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
        'selenium==2.53.1',
        'docker',
        'wrapt',
        'pymysql',
        'sqlalchemy',
        'psycopg2',
        'crayons',
        'blindspin',
        'pymysql'
    ],
)
