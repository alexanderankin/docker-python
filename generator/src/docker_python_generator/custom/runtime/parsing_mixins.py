"""Convenience parsers; generated dataclasses retain their structured JSON fields."""

import ipaddress
import re
from enum import Enum
from typing import TYPE_CHECKING, Self, get_args, get_type_hints


def host_binding_parts(value: str) -> tuple[str | None, str | None]:
    if not isinstance(value, str):
        raise TypeError(f"Invalid Binding: {value!r}")
    if not value:
        return None, None
    if value.startswith("["):
        match = re.fullmatch(r"\[([^\]]+)\](?::([^:]*))?", value)
        if not match:
            raise ValueError(f"Invalid Binding: {value!r}")
        ipaddress.IPv6Address(match[1])
        return match[1], match[2] or None
    if value.count(":") > 1:
        # An unbracketed IPv6 address is accepted only as an address, without a port.
        ipaddress.IPv6Address(value)
        return value, None
    if ":" in value:
        address, port = value.split(":")
        return address or None, port or None
    return (value, None) if "." in value else (None, value)


class BindingParsingMixin:
    host_ip: str | None
    host_port: str | None

    if TYPE_CHECKING:
        def __init__(self, *, host_ip: str | None = None, host_port: str | None = None) -> None: ...

    @classmethod
    def parse(cls, value: str) -> Self:
        try:
            address, port = host_binding_parts(value)
            if address:
                ipaddress.ip_address(address)
            if port and not re.fullmatch(r"\d+(?:-\d+)?", port):
                raise ValueError("Expected a host port or port range")
            return cls(host_ip=address, host_port=port)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid Binding: {value!r}") from error

    def __str__(self):
        address = self.host_ip or ""
        if ":" in address:
            address = f"[{address}]"
        return f"{address}:{self.host_port}" if address and self.host_port else address or self.host_port or ""


class DeviceParsingMixin:
    if TYPE_CHECKING:
        def __init__(self, *, path_on_host: str, path_in_container: str, cgroup_permissions: str) -> None: ...

    @classmethod
    def parse(cls, value: str) -> Self:
        try:
            parts = value.strip().split(":")
            if not parts[0] or len(parts) > 3:
                raise ValueError("Expected source[:destination][:permissions]")
            source, destination, permissions = parts[0], parts[0], "rwm"
            if len(parts) == 2:
                if parts[1] and all(char in "rwm" for char in parts[1]):
                    permissions = parts[1]
                else:
                    destination = parts[1]
            elif len(parts) == 3:
                destination, permissions = parts[1:]
            if (
                not destination
                or not permissions
                or any(c not in "rwm" for c in permissions)
                or len(set(permissions)) != len(permissions)
            ):
                raise ValueError("Invalid destination or device permissions")
            return cls(path_on_host=source, path_in_container=destination, cgroup_permissions=permissions)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid Device: {value!r}") from error


class RestartPolicyParsingMixin:
    name: Enum | None
    maximum_retry_count: int | None

    if TYPE_CHECKING:
        def __init__(self, *, name: Enum, maximum_retry_count: int) -> None: ...

    @classmethod
    def parse(cls, value: str) -> Self:
        try:
            parts = value.split(":")
            name = parts[0]
            if name not in ("no", "always", "unless-stopped", "on-failure") or len(parts) > 2:
                raise ValueError("Invalid policy")
            if len(parts) == 2 and name != "on-failure":
                raise ValueError("Retry count requires on-failure")
            retries = int(parts[1]) if len(parts) == 2 else 0
            if retries < 0:
                raise ValueError("Retry count must be nonnegative")
            # Resolve the enum through the generated field rather than importing a version package.
            annotation = get_type_hints(cls)["name"]
            enum = next((arg for arg in get_args(annotation) if arg is not type(None)), annotation)
            return cls(name=enum(name), maximum_retry_count=retries)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid RestartPolicy: {value!r}") from error

    def __str__(self):
        name = getattr(self.name, "value", self.name) or "no"
        return f"{name}:{self.maximum_retry_count}" if name == "on-failure" and self.maximum_retry_count else name
