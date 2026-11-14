"""String-valued container mount and link specifications."""

import re
from dataclasses import dataclass
from enum import Enum

from docker_python.core.json import json_creator, json_value


class AccessMode(str, Enum):
    RW = "rw"
    RO = "ro"


class SELContext(str, Enum):
    NONE = ""
    SHARED = "z"
    PRIVATE = "Z"


class PropagationMode(str, Enum):
    DEFAULT = ""
    SHARED = "shared"
    RSHARED = "rshared"
    SLAVE = "slave"
    RSLAVE = "rslave"
    PRIVATE = "private"
    RPRIVATE = "rprivate"


@dataclass(frozen=True)
class Volume:
    path: str

    @classmethod
    @json_creator
    def parse(cls, value: str | dict[str, str]) -> "Volume":
        path = value.get("path") if isinstance(value, dict) else value
        if not isinstance(path, str) or not path:
            raise ValueError(f"Invalid Volume: {value!r}")
        return cls(path)

    @json_value
    def __str__(self):
        return self.path


@dataclass(frozen=True)
class Volumes:
    volumes: tuple[Volume, ...]

    @classmethod
    @json_creator
    def from_primitive(cls, value: dict) -> "Volumes":
        return cls(tuple(Volume.parse(path) for path in value))

    @json_value
    def to_primitive(self):
        return {volume.path: {} for volume in self.volumes}


@dataclass(frozen=True)
class Bind:
    source: str
    destination: Volume
    access_mode: AccessMode = AccessMode.RW
    selinux: SELContext = SELContext.NONE
    nocopy: bool = False
    propagation: PropagationMode = PropagationMode.DEFAULT

    @classmethod
    @json_creator
    def parse(cls, value: str) -> "Bind":
        try:
            parts, start = [], 0
            for index, character in enumerate(value):
                # A single-letter named volume ("a:/data") is not a Windows source path.
                windows_source = re.match(r"/[^:]*:(?:[\\/]|[A-Za-z]:[\\/])", value[index + 1 :])
                drive_colon = (
                    index == start + 1
                    and value[start].isalpha()
                    and (
                        value[index + 1 : index + 2] == "\\"
                        or (value[index + 1 : index + 2] == "/" and (start > 0 or windows_source))
                    )
                )
                if character == ":" and not drive_colon:
                    parts.append(value[start:index])
                    start = index + 1
            parts.append(value[start:])
            if len(parts) not in (2, 3) or not parts[0] or not parts[1]:
                raise ValueError("Expected source:destination[:options]")
            mode, selinux, nocopy, propagation = AccessMode.RW, SELContext.NONE, False, PropagationMode.DEFAULT
            for option in parts[2].split(",") if len(parts) == 3 else []:
                if option in ("ro", "rw"):
                    mode = AccessMode(option)
                elif option in ("z", "Z"):
                    selinux = SELContext(option)
                elif option == "nocopy":
                    nocopy = True
                elif option in {p.value for p in PropagationMode if p.value}:
                    propagation = PropagationMode(option)
                else:
                    raise ValueError("Unknown bind option")
            return cls(parts[0], Volume(parts[1]), mode, selinux, nocopy, propagation)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid Bind: {value!r}") from error

    @json_value
    def __str__(self):
        options = [self.access_mode.value]
        if self.selinux.value:
            options.append(self.selinux.value)
        if self.nocopy:
            options.append("nocopy")
        if self.propagation.value:
            options.append(self.propagation.value)
        return f"{self.source}:{self.destination}:" + ",".join(options)


@dataclass(frozen=True)
class Binds:
    binds: tuple[Bind, ...]

    @classmethod
    @json_creator
    def from_primitive(cls, value: list[str]) -> "Binds":
        return cls(tuple(Bind.parse(item) for item in value))

    @json_value
    def to_primitive(self):
        return [str(bind) for bind in self.binds]


@dataclass(frozen=True)
class VolumesFrom:
    container: str
    access_mode: AccessMode = AccessMode.RW

    @classmethod
    @json_creator
    def parse(cls, value: str) -> "VolumesFrom":
        try:
            parts = value.split(":")
            if len(parts) not in (1, 2) or not parts[0]:
                raise ValueError("Expected container[:mode]")
            return cls(parts[0], AccessMode(parts[1]) if len(parts) == 2 else AccessMode.RW)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid VolumesFrom: {value!r}") from error

    @json_value
    def __str__(self):
        return f"{self.container}:{self.access_mode.value}"


@dataclass(frozen=True)
class Link:
    name: str
    alias: str

    @classmethod
    @json_creator
    def parse(cls, value: str) -> "Link":
        try:
            parts = value.split(":")
            if len(parts) != 2:
                raise ValueError("Expected name:alias")
            name, alias = (part.rsplit("/", 1)[-1] for part in parts)
            if not name or not alias:
                raise ValueError("Name and alias must not be empty")
            return cls(name, alias)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid Link: {value!r}") from error

    @json_value
    def __str__(self):
        return f"{self.name}:{self.alias}"


@dataclass(frozen=True)
class Links:
    links: tuple[Link, ...]

    @classmethod
    @json_creator
    def from_primitive(cls, value: list[str]) -> "Links":
        return cls(tuple(Link.parse(item) for item in value))

    @json_value
    def to_primitive(self):
        return [str(link) for link in self.links]
