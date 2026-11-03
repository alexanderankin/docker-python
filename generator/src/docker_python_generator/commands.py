"""Generate the list operations used by the prototype examples."""
from .models import GENERATED, snake
from .swagger import Swagger

LIST_OPERATIONS = {
    '/images/json': 'list_images',
    '/containers/json': 'list_containers',
    '/networks': 'list_networks',
}


def generate_list_commands(spec: Swagger) -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    files = {}
    commands = []
    for path, method in LIST_OPERATIONS.items():
        operation = spec['paths'][path]['get']
        name = operation['operationId'] + 'Command'
        module = snake(operation['operationId'])
        response_type = operation['operationId'] + 'Response200'
        fields, builders, query = [], [], []
        for parameter in operation.get('parameters', []):
            if parameter['in'] != 'query':
                raise ValueError(f'Unsupported list parameter: {parameter}')
            wire = parameter['name']
            attr = snake(wire)
            annotation = {'boolean': 'bool', 'integer': 'int', 'string': 'str'}[parameter['type']]
            fields.append(f'    {attr}: {annotation} | None = None')
            query.append(f'{wire!r}: self.{attr}')
            builders.append(f'''    def with_{attr}(self, value: {annotation}) -> "{name}":
        return replace(self, {attr}=value)
''')
        files[f'commands/{module}.py'] = GENERATED + f'''from dataclasses import dataclass, replace
from docker_python.core import Client, RequestBuilder, ResponseBuilder
from docker_python.core.models import from_wire
from ..models import {response_type}


@dataclass(frozen=True)
class {name}:
    client: Client
{chr(10).join(fields)}

{chr(10).join(builders)}
    def execute(self) -> {response_type}:
        return self.client.execute(
            RequestBuilder("GET", {path!r}, query={{{', '.join(query)}}}),
            ResponseBuilder(lambda data: from_wire({response_type}, data)),
        )
'''
        commands.append((module, name, method))
    return files, commands
