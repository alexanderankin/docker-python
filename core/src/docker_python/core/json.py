"""Opt-in JSON conversion hooks for handwritten model types."""
from typing import Any, TypeVar

D = TypeVar('D')
CREATOR = '__docker_json_creator__'
VALUE = '__docker_json_value__'


def json_creator(method: D) -> D:
    """Mark a classmethod or staticmethod that constructs a value from JSON."""
    target = method.__func__ if isinstance(method, (classmethod, staticmethod)) else method
    setattr(target, CREATOR, True)
    return method


def json_value(method: D) -> D:
    """Mark an instance method that returns the value's JSON representation."""
    setattr(method, VALUE, True)
    return method


def json_method(cls: type, marker: str) -> str | None:
    found = []
    seen = set()
    for base in cls.__mro__:
        for name, descriptor in vars(base).items():
            if name in seen:
                continue
            seen.add(name)
            method: Any = descriptor.__func__ if isinstance(descriptor, (classmethod, staticmethod)) else descriptor
            if getattr(method, marker, False):
                if marker == CREATOR and not isinstance(descriptor, (classmethod, staticmethod)):
                    raise TypeError(f'{cls.__name__}.{name}: @json_creator requires @classmethod or @staticmethod')
                found.append(name)
    if len(found) > 1:
        raise TypeError(f'{cls.__name__} defines multiple JSON conversion methods: {found}')
    return found[0] if found else None
