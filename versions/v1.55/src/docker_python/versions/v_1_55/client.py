# Generated from Docker Engine Swagger; regenerate via docker_python_generator.
from docker_python.core import Client, Transport
from .commands import SystemVersionCommand, ImageListCommand, ContainerListCommand, NetworkListCommand


class DockerClient(Client):
    def __init__(self, transport: Transport):
        super().__init__(transport, '1.55')

    def system_version(self) -> SystemVersionCommand:
        return SystemVersionCommand(self)

    def list_images(self) -> ImageListCommand:
        return ImageListCommand(self)

    def list_containers(self) -> ContainerListCommand:
        return ContainerListCommand(self)

    def list_networks(self) -> NetworkListCommand:
        return NetworkListCommand(self)
