from dataclasses import dataclass
from enum import Enum


class Unset(Enum):
    VALUE = 'unset'


UNSET = Unset.VALUE


@dataclass(frozen=True)
class ParameterSpec:
    attribute: str
    name: str
    location: str
    required: bool = False
    collection_format: str | None = None
    is_file: bool = False
