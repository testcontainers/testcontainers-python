docker_base_url = 'unix://var/run/docker.sock'
max_tries = 60
sleep_time = 1

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
    'bind_ports': {5900: 5901},
    'env': ['no_proxy=localhost', 'HUB_ENV_no_proxy=localhost']
}
