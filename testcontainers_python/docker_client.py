import logging

from docker import Client

from testcontainers_python import config


class DockerClient(object):
    def __init__(self, base_url=config.docker_base_url):
        self._cli = Client(base_url)

    def run(self, image, bind_ports=None, name=None, links=None, env=None):
        self.pull_image(image)
        container = self._create_container(image, bind_ports=bind_ports, name=name, env=env)
        self._cli.start(container, publish_all_ports=True, port_bindings=bind_ports, links=links)
        return container

    def pull_image(self, image):
        if not self.image_exists(image):
            logging.warning("Downloading image {}".format(image))
            stream = self.pull(image)
            for line in stream:
                logging.warning(line)
        else:
            logging.warning("Image {} already exists".format(image))

    def pull(self, name):
        return self._cli.pull(name, stream=True)

    def _create_container(self, image,
                          bind_ports=None,
                          name=None,
                          env=None):
        for container in self.filter_containers(name):  # filter containers and remove to void name conflict error
            self.remove(container, True)

        host_config = self._cli.create_host_config(port_bindings=bind_ports)
        return self._cli.create_container(image=image,
                                          ports=self._get_exposed_ports(bind_ports),
                                          host_config=host_config,
                                          name=name,
                                          environment=env)

    def _get_exposed_ports(self, ports):
        return dict(ports).keys() if ports else None

    def filter_containers(self, name):
        for container in self._filter_by_name(name):
            yield container['Id']

    def _filter_by_name(self, name):
        return self._cli.containers(all=True, filters={"name": name}) if name else []

    def inspect(self, container):
        return self._cli.inspect_container(container)

    def get_host_info(self, container):
        return self.inspect(container)

    def get_containers(self):
        return self._cli.containers()

    def remove_image(self, name, force=False):
        self._cli.remove_image(name, force)

    def image_exists(self, name):
        lists = []
        for im in self.images():
            lists.append(im["RepoTags"])
        return name in [item for sublist in lists for item in sublist]

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
        logging.warning("Container removed {}".format(container['Id']))

    def images(self):
        return self._cli.images()

    def stop_all(self):
        for cont in self.get_containers():
            self.stop(cont)

    def remove_all(self):
        for cont in self.get_containers():
            self.remove(cont, True)
