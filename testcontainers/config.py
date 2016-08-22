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

##################
# General config #
##################

docker_base_url = 'unix://var/run/docker.sock'
max_tries = 120
sleep_time = 1

####################
# My SQL Container #
####################

mysql_db = {
    "host": "0.0.0.0",
    "user": "root",
    "passwd": "test",
    "db": "test"
}

my_sql_container = {
    'bind_ports': {3306: 3306},
    'env': {
        "MYSQL_ROOT_PASSWORD": mysql_db['passwd'],
        "MYSQL_DATABASE": mysql_db['db']
    },
    "name": "mysql"
}

######################
# Postgres container #
######################

postgres_db = {
    "host": "0.0.0.0",
    "user": "root",
    "passwd": "test",
    "db": "test"
}

postgres_container = {
    "env": {
        "POSTGRES_USER": postgres_db["user"],
        "POSTGRES_PASSWORD": postgres_db["passwd"],
        "POSTGRES_DB": postgres_db["db"]
    },
    "bing_ports": {5432: 5432},
    "name": "postgres"
}

######################
# Selenium container #
######################

selenium_hub_host = "localhost"

hub = {
    'image': 'selenium/hub:2.53.0',
    'bind_ports': {4444: 4444},
    'name': 'selenium-hub'
}

firefox_node = {
    'image': 'selenium/node-firefox-debug:2.53.0',
    'links': {'selenium-hub': 'hub'},
    'bind_ports': {5900: 5900},
    'env': ['no_proxy=localhost', 'HUB_ENV_no_proxy=localhost']
}

chrome_node = {
    'image': 'selenium/node-chrome-debug:2.53.0',
    'links': {'selenium-hub': 'hub'},
    'bind_ports': {5901: 5900},
    'env': ['no_proxy=localhost', 'HUB_ENV_no_proxy=localhost']
}
