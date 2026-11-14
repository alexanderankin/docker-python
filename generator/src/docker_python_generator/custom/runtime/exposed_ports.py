"""Ports expressed as Python values and Docker's primitive JSON forms."""

from dataclasses import dataclass
from enum import Enum

from docker_python.core.json import json_creator, json_value


class InternetProtocol(str, Enum):
    TCP = "tcp"
    UDP = "udp"
    SCTP = "sctp"
    DEFAULT = TCP

    @classmethod
    @json_creator
    def parse(cls, value: str) -> "InternetProtocol":
        try:
            return cls(value.lower())
        except (AttributeError, ValueError) as error:
            raise ValueError(f"Invalid InternetProtocol: {value!r}") from error

    @json_value
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExposedPort:
    port: int
    protocol: InternetProtocol = InternetProtocol.TCP

    def __post_init__(self):
        object.__setattr__(self, "protocol", InternetProtocol.parse(self.protocol))

    @classmethod
    @json_creator
    def parse(cls, value: str) -> "ExposedPort":
        try:
            parts = value.split("/")
            if len(parts) not in (1, 2):
                raise ValueError("Expected port[/protocol]")
            return cls(int(parts[0]), InternetProtocol.parse(parts[1]) if len(parts) == 2 else InternetProtocol.TCP)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid ExposedPort: {value!r}") from error

    @json_value
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
