from docker import Client
import logging

from testcontainers_python import config


class DockerClient(object):
    def __init__(self, base_url=config.docker_base_url):
        self.cli = Client(base_url)

    def run(self, image, bind_ports=None, name=None, links=None, env=None):
        if not self.image_exists(image):
            logging.warning("Downloading image {}".format(image))
            stream = self.pull(image)
            for line in stream:
                logging.warning(line)
        host_config = self.cli.create_host_config(port_bindings=bind_ports)

        container = self.cli.create_container(image=image,
                                              ports=self._expose_ports(bind_ports),
                                              host_config=host_config,
                                              name=name,
                                              environment=env)
        self.cli.start(container, publish_all_ports=True, port_bindings=bind_ports, links=links)
        return container

    def _expose_ports(self, ports):
        return dict(ports).keys() if ports else None

    def pull(self, name):
        return self.cli.pull(name, stream=True)

    def inspect(self, container):
        return self.cli.inspect_container(container)

    def get_host_info(self, container):
        return self.inspect(container)

    def get_containers(self):
        return self.cli.containers()

    def remove_image(self, name, force=False):
        self.cli.remove_image(name, force)

    def image_exists(self, name):
        lists = []
        for im in self.images():
            lists.append(im["RepoTags"])
        return name in [item for sublist in lists for item in sublist]

    def stop(self, container):
        self.cli.stop(container)

    def remove(self, container, force=False):
        """
        Stop and remote container
        :param container:
        :param force:
        :return:
        """
        self.cli.remove_container(container, force)

    def images(self):
        return self.cli.images()

    def stop_all(self):
        for cont in self.get_containers():
            self.stop(cont)
            logging.warning("Container stopped {}".format(cont['Id']))
