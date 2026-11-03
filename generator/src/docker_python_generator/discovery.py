"""Walk Swagger operations once, resolving shared parameters and responses."""
from dataclasses import dataclass
import re
from typing import Any, Iterator, cast

from .swagger import Operation, Parameter, Response, Schema, Swagger

HTTP_METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch'}


def pascal(value: str) -> str:
    return ''.join(part[:1].upper() + part[1:] for part in re.split(r'[^a-zA-Z0-9]+', value) if part)


@dataclass(frozen=True)
class OperationDefinition:
    path: str
    method: str
    operation: Operation
    parameters: list[Parameter]
    responses: dict[str, Response]

    @property
    def name(self) -> str:
        return self.operation['operationId']

    def parameter_model(self, parameter: Parameter) -> str:
        prefix = pascal(self.name)
        if parameter['in'] == 'body':
            return prefix + 'Request'
        return prefix + pascal(parameter['in']) + pascal(parameter['name'])

    def response_model(self, status: str) -> str:
        return pascal(self.name) + 'Response' + pascal(status)


def parameter_schema(parameter: Parameter) -> Schema:
    if parameter['in'] == 'body':
        return parameter['schema']
    return cast(Schema, {key: value for key, value in parameter.items()
                         if key not in {'name', 'in', 'required'}})


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

    def operations(self) -> Iterator[OperationDefinition]:
        seen = set()
        for path, path_item in self.spec['paths'].items():
            path_item = self.resolve(path_item)
            shared = path_item.get('parameters', [])
            for method, raw in path_item.items():
                if method not in HTTP_METHODS:
                    continue
                operation = cast(Operation, self.resolve(raw))
                if operation['operationId'] in seen:
                    raise ValueError(f'Duplicate operationId: {operation["operationId"]}')
                seen.add(operation['operationId'])
                parameters = {}
                for raw_parameter in [*shared, *operation.get('parameters', [])]:
                    parameter = cast(Parameter, self.resolve(raw_parameter))
                    parameters[(parameter['name'], parameter['in'])] = parameter
                responses = {str(status): cast(Response, self.resolve(response))
                             for status, response in operation['responses'].items()}
                yield OperationDefinition(path, method.upper(), operation, list(parameters.values()), responses)

    def model_name(self, name: str, schema: Schema) -> str:
        if '$ref' in schema and len(schema) == 1:
            ref = schema['$ref']
            if ref.startswith('#/definitions/') and ref.removeprefix('#/definitions/') in self.spec['definitions']:
                return ref.removeprefix('#/definitions/')
        return name

    def collect(self) -> dict[str, Schema]:
        schemas = dict(self.spec['definitions'])

        def add(name: str, schema: Schema) -> None:
            if '$ref' in schema and len(schema) == 1 and schema['$ref'].startswith('#/definitions/'):
                target = schema['$ref'].removeprefix('#/definitions/')
                if target not in self.spec['definitions']:
                    raise ValueError(f'Unknown definition: {target}')
                return
            if name in schemas:
                raise ValueError(f'Operation type name collides with another model: {name}')
            schemas[name] = schema

        for definition in self.operations():
            for parameter in definition.parameters:
                add(definition.parameter_model(parameter), parameter_schema(parameter))
            for status, response in definition.responses.items():
                name = definition.response_model(status)
                if 'schema' in response:
                    add(name, response['schema'])
                for header, schema in response.get('headers', {}).items():
                    add(name + 'Header' + pascal(header), schema)
        return schemas
