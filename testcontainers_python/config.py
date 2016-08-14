docker_base_url = 'unix://var/run/docker.sock'
max_tries = 60
sleep_time = 1
hub = {'image': 'selenium/hub:2.53.0', 'bind_ports': {4444: 4444}, 'name': 'selenium-hub'}
ff_node = {'image': 'selenium/node-firefox:2.53.0', 'links': {'selenium-hub': 'hub'}}
chrome_node = {'image': 'selenium/node-chrome:2.53.0', 'links': {'selenium-hub': 'hub'}}
