import logging
from time import sleep

from docker import Client

from testcontainers import config
from testcontainers.brogress_bar import ConsoleProgressBar


class DockerClient(object):
    def __init__(self, base_url=config.docker_base_url):
        self._cli = Client(base_url)
        self._containers = []

    def run(self, image, bind_ports=None, name=None, links=None, env=None):
        """
        Pulls image if not exists and run
        :param image:
        :param bind_ports:
        :param name:
        :param links:
        :param env:
        :return:
        """
        self.pull_image(image)
        container = self._create_container(image, bind_ports=bind_ports, name=name, env=env)
        self._cli.start(container, publish_all_ports=True, port_bindings=bind_ports, links=links)
        self._containers.append(container)
        return container

    def pull_image(self, image):
        """
        Pulls image if not exists
        :param image:
        :return:
        """
        if not self.image_exists(image):
            logging.warning("Downloading image {}".format(image))
            stream = self._pull(image)
            bar = ConsoleProgressBar().bar
            for _ in bar(range(len(list(stream)))):
                sleep(0.1)
        else:
            logging.warning("Image {} already exists".format(image))

    def _pull(self, name):
        """
        Pulls image
        :param name:
        :return:
        """
        return self._cli.pull(name, stream=True)

    def _create_container(self, image,
                          bind_ports=None,
                          name=None,
                          env=None,
                          volumes=None):
        """
        Creates new container
        :param image:
        :param bind_ports:
        :param name:
        :param env:
        :return:
        """
        for container in self.filter_containers(name):  # filter containers and remove to void name conflict error
            self.remove(container, True)

        host_config = self._cli.create_host_config(port_bindings=bind_ports, binds=volumes)
        return self._cli.create_container(image=image,
                                          ports=self._get_exposed_ports(bind_ports),
                                          volumes=self._get_volumes_to_mount(volumes),
                                          host_config=host_config,
                                          name=name,
                                          environment=env)

    def _get_exposed_ports(self, ports):
        return dict(ports).values() if ports else None

    def _get_volumes_to_mount(self, volumes):
        return dict(volumes).values() if volumes else None

    def filter_containers(self, name):
        """
        Filter containers by name
        :param name:
        :return:
        """
        for container in self._filter_by_name(name):
            yield container['Id']

    def _filter_by_name(self, name):
        """
        :param name:
        :return:
        """
        return self._cli.containers(all=True, filters={"name": name}) if name else []

    def inspect(self, container):
        """
        :param container:
        :return:
        """
        return self._cli.inspect_container(container)

    def get_host_info(self, container):
        return self.inspect(container)

    def get_running_containers(self):
        return self._cli.containers()

    def remove_image(self, name, force=False):
        self._cli.remove_image(name, force)

    def image_exists(self, name):
        lists = []
        for im in self.images():
            lists.append(im["RepoTags"])
        return name in [item for sublist in lists for item in sublist]

    def port(self, container, port):
        return self._cli.port(container, port)

    def stop(self, container):
        self._cli.stop(container)
        logging.warning("Container stopped {}".format(container['Id']))

    def remove(self, container, force=False):
        """
        Stop and remote container
        :param container:
        :param force:
        :return:
        """
        self._cli.remove_container(container, force=force)
        if type(container) == type({}):
            logging.warning("Container removed {}".format(container['Id']))
        else:
            logging.warning("Container removed {}".format(container))

    def images(self):
        return self._cli.images()

    def stop_all(self):
        for cont in self.get_running_containers():
            self.stop(cont)

    def stop_all_spawned(self):
        for cont in self._containers:
            self.stop(cont)

    def remove_all(self):
        for cont in self.get_running_containers():
            self.remove(cont, True)

    def remove_all_spawned(self):
        for cont in self._containers:
            self.remove(cont, True)
