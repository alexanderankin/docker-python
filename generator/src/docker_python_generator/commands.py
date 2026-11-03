"""Emit one typed command for each operation in Swagger paths."""
from dataclasses import dataclass
from pathlib import Path

from .discovery import OperationDefinition, SchemaDiscovery, parameter_schema
from .models import GENERATED, class_name, snake
from .swagger import Parameter, Swagger


def union(types: list[str]) -> str:
    types = list(dict.fromkeys(types))
    if not types or 'Any' in types:
        return 'Any'
    return types[0] if len(types) == 1 else f'Union[{", ".join(types)}]'


@dataclass
class CommandGenerator:
    spec: Swagger

    def parameter_type(self, discovery: SchemaDiscovery, operation: OperationDefinition, parameter: Parameter) -> str:
        model = discovery.model_name(operation.parameter_model(parameter), parameter_schema(parameter))
        return 'models.' + class_name(model)

    def response_type(self, discovery: SchemaDiscovery, operation: OperationDefinition, status: str) -> str:
        response = operation.responses[status]
        if 'schema' in response:
            model = discovery.model_name(operation.response_model(status), response['schema'])
            return 'models.' + class_name(model)
        if status == '204' or operation.method == 'HEAD':
            return 'None'
        return 'Any'  # Swagger does not specify a body; preserve text/binary responses.

    def generate(self, output: Path) -> None:
        discovery = SchemaDiscovery(self.spec)
        directory = output / 'commands'
        directory.mkdir(parents=True, exist_ok=True)
        exports, client_methods = [], []
        seen_modules, seen_methods = set(), set()
        for operation in discovery.operations():
            name = class_name(operation.name) + 'Command'
            module = snake(operation.name)
            if module in seen_modules:
                raise ValueError(f'Command module collision: {module}')
            seen_modules.add(module)
            fields, builders, parameters, arguments, assignments = [], [], [], [], []
            used = {'client', 'build_request', 'execute', 'execute_response', 'execute_stream'}
            for parameter in operation.parameters:
                attribute = snake(parameter['name'])
                if attribute in used:
                    attribute = snake(parameter['in']) + '_' + attribute
                if attribute in used:
                    raise ValueError(f'Parameter attribute collision: {operation.name}.{attribute}')
                used.add(attribute)
                annotation = self.parameter_type(discovery, operation, parameter)
                fields.append(f'    {attribute}: {annotation} | Unset = UNSET')
                arguments.append(f'{attribute}: {annotation} | Unset = UNSET')
                assignments.append(f'{attribute}={attribute}')
                parameters.append(
                    f'ParameterSpec({attribute!r}, {parameter["name"]!r}, {parameter["in"]!r}, '
                    f'required={parameter.get("required", False)!r}, '
                    f'collection_format={parameter.get("collectionFormat", "csv" if parameter.get("type") == "array" else None)!r}, '
                    f'is_file={parameter.get("type") == "file"!r})'
                )
                builders.append(f'''    def with_{attribute}(self, value: {annotation}) -> "{name}":
        return replace(self, {attribute}=value)
''')
            successes, decoders, errors, error_decoders, returns = [], [], [], [], []
            for status in operation.responses:
                if status == 'default':
                    continue
                code = int(status)
                annotation = self.response_type(discovery, operation, status)
                decoder = ('lambda body: None' if annotation == 'None' else
                           'lambda body: body' if annotation == 'Any' else
                           f'lambda body: from_wire({annotation}, body)')
                if 200 <= code < 300 or code == 101:
                    successes.append(code)
                    returns.append(annotation)
                    decoders.append(f'{code}: {decoder}')
                else:
                    errors.append(f'{code}: ERROR_TYPES.get({code}, DockerError)')
                    error_decoders.append(f'{code}: {decoder}')
            default_error_decoder = 'lambda body: body'
            if 'default' in operation.responses:
                annotation = self.response_type(discovery, operation, 'default')
                if annotation not in ('Any', 'None'):
                    default_error_decoder = f'lambda body: from_wire({annotation}, body)'
            result_type = union(returns)
            consumes = operation.operation.get('consumes', self.spec.get('consumes', []))
            content_type = next((parameter['default'] for parameter in operation.parameters
                                 if parameter['in'] == 'header'
                                 and parameter['name'].lower() == 'content-type'
                                 and 'default' in parameter), consumes[0] if consumes else None)
            source = GENERATED + f'''from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, ClassVar, Union
from docker_python.core import DockerError, ERROR_TYPES, ResponseBuilder
from docker_python.core.commands import Command
from docker_python.core.models import from_wire, bind_model_types
from docker_python.core.parameters import ParameterSpec, UNSET, Unset
from .. import models

bind_model_types(models.__name__, globals())


@dataclass(frozen=True, kw_only=True)
class {name}(Command[{result_type}]):
    METHOD: ClassVar[str] = {operation.method!r}
    PATH: ClassVar[str] = {operation.path!r}
    CONTENT_TYPE: ClassVar[str | None] = {content_type!r}
    PARAMETERS: ClassVar[tuple[ParameterSpec, ...]] = ({', '.join(parameters)}{',' if parameters else ''})
    RESPONSE: ClassVar[ResponseBuilder] = ResponseBuilder(
        decode=lambda body: body,
        statuses={tuple(successes)!r},
        decoders={{{', '.join(decoders)}}},
        errors={{{', '.join(errors)}}},
        error_decoders={{{', '.join(error_decoders)}}},
        default_error_decoder={default_error_decoder},
    )
{chr(10).join(fields)}

{chr(10).join(builders)}'''
            (directory / (module + '.py')).write_text(source)
            exports.append((module, name))
            method = snake(operation.name)
            if method in seen_methods:
                raise ValueError(f'Client method collision: {method}')
            seen_methods.add(method)
            signature = ', *, ' + ', '.join(arguments) if arguments else ''
            values = ', ' + ', '.join(assignments) if assignments else ''
            client_methods.append(f'''    def {method}(self{signature}) -> commands.{name}:
        return commands.{name}(self{values})
''')
            # OperationIds remain canonical; List operations also get verb-first convenience names.
            if operation.name.endswith('List'):
                alias = 'list_' + snake(operation.name[:-4]) + 's'
                if alias in seen_methods:
                    raise ValueError(f'Client alias collision: {alias}')
                seen_methods.add(alias)
                client_methods.append(f'    {alias} = {method}\n')
        init = GENERATED + ''.join(f'from .{module} import {name}\n' for module, name in exports)
        init += '\n__all__ = ' + repr([name for _, name in exports]) + '\n'
        (directory / '__init__.py').write_text(init)
        client = GENERATED + f'''from __future__ import annotations

from docker_python.core import Client, Transport
from docker_python.core.models import bind_model_types
from docker_python.core.parameters import UNSET, Unset
from . import commands, models

bind_model_types(models.__name__, globals())


class DockerClient(Client):
    def __init__(self, transport: Transport):
        super().__init__(transport, {self.spec['info']['version']!r})

'''
        (output / 'client.py').write_text(client + '\n'.join(client_methods))
        (output / '__init__.py').write_text(GENERATED + 'from .client import DockerClient\n\n__all__ = ["DockerClient"]\n')
