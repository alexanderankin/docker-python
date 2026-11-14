"""Handwritten runtime types copied into each compatible generated API package."""

from dataclasses import dataclass

from docker_python.core.json import json_creator, json_value


@dataclass(frozen=True)
class ExposedPort:
    port: int
    protocol: str = "tcp"

    @classmethod
    def parse(cls, value: str) -> "ExposedPort":
        port, protocol = value.split("/", 1)
        return cls(int(port), protocol)

    def __str__(self) -> str:
        return f"{self.port}/{self.protocol}"


@dataclass(frozen=True)
class ExposedPorts:
    ports: tuple[ExposedPort, ...]

    @classmethod
    @json_creator
    def from_primitive(cls, value: dict[str, object]) -> "ExposedPorts":
        return cls(tuple(ExposedPort.parse(key) for key in value))

    @json_value
    def to_primitive(self) -> dict[str, object]:
        return {str(port): {} for port in self.ports}
