"""Collect named definitions and schemas declared inline by operations."""
from dataclasses import dataclass
import re
from typing import Any, cast

from .swagger import Schema, Swagger

HTTP_METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch'}


def pascal(value: str) -> str:
    return ''.join(part[:1].upper() + part[1:] for part in re.split(r'[^a-zA-Z0-9]+', value) if part)


@dataclass
class SchemaDiscovery:
    spec: Swagger

    def resolve(self, value: dict[str, Any]) -> dict[str, Any]:
        seen: set[str] = set()
        while '$ref' in value:
            ref = value['$ref']
            if not ref.startswith('#/') or ref in seen:
                raise ValueError(f'Unsupported or cyclic Swagger reference: {ref}')
            seen.add(ref)
            target: Any = self.spec
            for token in ref[2:].split('/'):
                target = target[token.replace('~1', '/').replace('~0', '~')]
            value = target
        return value

    def collect(self) -> dict[str, Schema]:
        schemas = dict(self.spec['definitions'])

        def add(name: str, schema: Schema) -> None:
            # A direct definition reference already has its own module.
            if '$ref' in schema and len(schema) == 1:
                ref = schema['$ref']
                if ref.startswith('#/definitions/') and ref.removeprefix('#/definitions/') in schemas:
                    return
            if name in schemas:
                raise ValueError(f'Operation type name collides with another model: {name}')
            schemas[name] = schema

        for path_item in self.spec['paths'].values():
            path_item = self.resolve(path_item)
            shared = path_item.get('parameters', [])
            for method, operation in path_item.items():
                if method not in HTTP_METHODS:
                    continue
                operation = self.resolve(operation)
                prefix = pascal(operation['operationId'])
                # Operation parameters override path parameters by (name, location).
                parameters = {}
                for parameter in [*shared, *operation.get('parameters', [])]:
                    parameter = self.resolve(parameter)
                    parameters[(parameter['name'], parameter['in'])] = parameter
                for (name, location), parameter in parameters.items():
                    if location == 'body':
                        add(prefix + 'Request', parameter['schema'])
                    else:
                        schema = cast(Schema, {key: value for key, value in parameter.items()
                                             if key not in {'name', 'in', 'required'}})
                        add(prefix + pascal(location) + pascal(name), schema)
                for status, response in operation.get('responses', {}).items():
                    response = self.resolve(response)
                    response_name = prefix + 'Response' + pascal(str(status))
                    if 'schema' in response:
                        add(response_name, response['schema'])
                    for header, schema in response.get('headers', {}).items():
                        add(response_name + 'Header' + pascal(header), schema)
        return schemas
