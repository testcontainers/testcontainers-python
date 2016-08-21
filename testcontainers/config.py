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
    "image": "postgres:latest",
    "env": {
        "POSTGRES_USER": "root",
        "POSTGRES_PASSWORD": "secret",
        "POSTGRES_DB": "test"
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
