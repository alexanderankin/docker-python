"""Host bindings and complete published-port mappings."""

from dataclasses import dataclass, field

from docker_python.core.json import json_creator, json_value

from .binding import Binding
from .exposed_ports import ExposedPort


@dataclass(frozen=True)
class PortBinding:
    binding: Binding
    exposed_port: ExposedPort

    @classmethod
    def parse(cls, value: str) -> "PortBinding":
        try:
            if value.startswith("["):
                end = value.index("]")
                tail = value[end + 1 :]
                if not tail.startswith(":") or ":" not in tail[1:]:
                    raise ValueError("Expected [IPv6]:host-port:container-port")
                host_port, exposed = tail[1:].split(":")
                host = value[: end + 1] + ":" + host_port
            else:
                parts = value.split(":")
                if not 1 <= len(parts) <= 3:
                    raise ValueError("Expected [address:][host-port:]container-port")
                host, exposed = ":".join(parts[:-1]), parts[-1]
            return cls(Binding.parse(host), ExposedPort.parse(exposed))
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid PortBinding: {value!r}") from error

    def __str__(self):
        # Keep the empty host-port slot when an address selects a dynamic port.
        host = str(self.binding)
        if self.binding.host_ip and not self.binding.host_port:
            host += ":"
        return f"{host}:{self.exposed_port}" if host else str(self.exposed_port)


@dataclass
class Ports:
    bindings: dict[ExposedPort, tuple[Binding, ...] | None] = field(default_factory=dict)

    @classmethod
    def from_bindings(cls, *bindings: PortBinding) -> "Ports":
        result = cls()
        for binding in bindings:
            previous = result.bindings.get(binding.exposed_port) or ()
            result.bindings[binding.exposed_port] = previous + (binding.binding,)
        return result

    @classmethod
    @json_creator
    def from_primitive(cls, value: dict) -> "Ports":
        return cls(
            {
                ExposedPort.parse(port): None
                if bindings is None
                else tuple(Binding.from_wire(item) for item in bindings)
                for port, bindings in value.items()
            }
        )

    @json_value
    def to_primitive(self) -> dict:
        return {
            str(port): None
            if bindings is None
            else [{"HostIp": binding.host_ip or "", "HostPort": binding.host_port or ""} for binding in bindings]
            for port, bindings in self.bindings.items()
        }
