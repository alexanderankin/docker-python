"""Shared conversion between generated dataclass models and Docker JSON."""
from dataclasses import fields, is_dataclass
from enum import Enum
from importlib import import_module
from types import UnionType
from typing import Any, ForwardRef, Union, get_args, get_origin, get_type_hints


class Model:
    @classmethod
    def from_wire(cls, data: dict[str, Any]):
        hints = get_type_hints(cls)
        return cls(**{
            item.name: from_wire(hints[item.name], data[item.metadata['wire_name']])
            for item in fields(cls) if item.metadata['wire_name'] in data
        })

    def to_wire(self) -> dict[str, Any]:
        return to_wire(self)


def from_wire(annotation: Any, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(annotation, ForwardRef):
        namespace = vars(import_module(annotation.__forward_module__))
        def resolve():
            pass
        resolve.__annotations__ = {"return": annotation}
        annotation = get_type_hints(resolve, globalns=namespace)['return']
    origin, args = get_origin(annotation), get_args(annotation)
    if origin in (Union, UnionType):
        # Generated unions currently express nullable types only.
        return from_wire(next(arg for arg in args if arg is not type(None)), value)
    if origin is list:
        return [from_wire(args[0], item) for item in value]
    if origin is dict:
        return {key: from_wire(args[1], item) for key, item in value.items()}
    if isinstance(annotation, type):
        if issubclass(annotation, Model):
            return annotation.from_wire(value)
        if issubclass(annotation, Enum):
            return annotation(value)
    return value


def to_wire(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.metadata.get('wire_name', item.name): to_wire(getattr(value, item.name))
            for item in fields(value) if getattr(value, item.name) is not None
        }
    if isinstance(value, dict):
        return {key: to_wire(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_wire(item) for item in value]
    return value


def bind_model_namespace(package_name: str, modules: list[str], exports: list[str]) -> None:
    """Link annotations after all models load, without imports between models.

    Each generated model module gets its version's complete type namespace.
    This allows ordinary get_type_hints() and recursive aliases to resolve.
    """
    package = import_module(package_name)
    namespace = {name: getattr(package, name) for name in exports}
    for module in modules:
        vars(import_module(f'{package_name}.{module}')).update(namespace)


def bind_model_types(package_name: str, namespace: dict[str, Any]) -> None:
    """Expose alias targets to annotation consumers in commands and clients."""
    package = import_module(package_name)
    namespace.update({name: getattr(package, name) for name in package.__all__})
