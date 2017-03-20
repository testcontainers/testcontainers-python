import os

import yaml


def get_env(env, default):
    return os.environ.get(env, default)


MAX_TRIES = int(get_env("TC_MAX_TRIES", 120))
SLEEP_TIME = int(get_env("TC_POOLING_INTERVAL", 1))


class Configuration(object):
    def __init__(self, filename="config.yml"):
        with open(filename, 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

    def get(self, section):
        return self.cfg[section]
