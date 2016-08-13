from docker import Client
from docker.errors import NotFound
import logging


class DockerManager(object):
    def __init__(self, base_url='unix://var/run/docker.sock'):
        self.cli = Client(base_url)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for cont in self.get_containers():
            self.stop(cont)
            self.remove(cont)

    def run(self, image, ports=None, port_bindings=None, name=None, links=None):
        if not self.image_exists(image):
            logging.warning("Downloading image {}".format(image))
            stream = self.pull(image)
            for line in stream:
                print(line)
        host_config = self.cli.create_host_config(port_bindings=port_bindings)
        container = self.cli.create_container(image=image, ports=ports, host_config=host_config, name=name)
        self.cli.start(container, publish_all_ports=True, port_bindings=port_bindings, links=links)
        return container

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

    def remove(self, container):
        """
        Stop and remote container
        :param container:
        :return:
        """
        self.stop(container)
        self.cli.remove_container(container)

    def images(self):
        return self.cli.images()
