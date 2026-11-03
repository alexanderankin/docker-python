"""The Swagger 2.0 shapes consumed by the prototype generator."""
from pathlib import Path
from typing import Any, NotRequired, TypedDict, cast

import yaml


Schema = TypedDict('Schema', {
    '$ref': str,
    'type': str,
    'format': str,
    'description': str,
    'properties': dict[str, 'Schema'],
    'required': list[str],
    'items': 'Schema',
    'additionalProperties': 'Schema | bool',
    'allOf': list['Schema'],
    'enum': list[str | int | float | bool | None],
    'default': Any,
    'x-nullable': bool,
}, total=False)


Parameter = TypedDict('Parameter', {
    '$ref': str,
    'name': str,
    'in': str,
    'required': bool,
    'schema': Schema,
    'type': str,
    'items': Schema,
    'description': str,
}, total=False)


class Response(TypedDict, total=False):
    description: str
    schema: Schema
    headers: dict[str, Schema]


class Operation(TypedDict):
    operationId: str
    parameters: NotRequired[list[Parameter]]
    responses: dict[str, Response]


PathItem = TypedDict('PathItem', {
    '$ref': str,
    'parameters': list[Parameter],
    'get': Operation,
    'put': Operation,
    'post': Operation,
    'delete': Operation,
    'options': Operation,
    'head': Operation,
    'patch': Operation,
}, total=False)


class Info(TypedDict):
    version: str
    title: str


class Swagger(TypedDict):
    swagger: str
    info: Info
    definitions: dict[str, Schema]
    paths: dict[str, "PathItem"]
    parameters: NotRequired[dict[str, Parameter]]
    responses: NotRequired[dict[str, Response]]
    basePath: NotRequired[str]


def load_spec(path: Path) -> Swagger:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or data.get('swagger') != '2.0':
        raise ValueError('Expected a Swagger 2.0 document')
    for key in ('info', 'definitions', 'paths'):
        if not isinstance(data.get(key), dict):
            raise ValueError(f'Missing Swagger mapping: {key}')
    return cast(Swagger, data)
