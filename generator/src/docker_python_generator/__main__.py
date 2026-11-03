"""Generate Swagger models and prototype version/list commands."""
import argparse
from pathlib import Path
from .swagger import load_spec
from .commands import generate_list_commands
from .discovery import SchemaDiscovery
from .models import GENERATED, ModelGenerator
from docker_python.core import RequestBuilder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    spec = load_spec(args.spec)
    version = spec["info"]["version"]
    operation = spec["paths"]["/version"]["get"]
    assert operation["operationId"] == "SystemVersion"
    request = RequestBuilder("GET", "/version")
    module = args.output / "src" / "docker_python" / "versions" / ("v_" + version.replace(".", "_"))
    module.mkdir(parents=True, exist_ok=True)
    generated = GENERATED
    files = {
        "commands/system_version.py": generated + f'''from dataclasses import dataclass
from docker_python.core import Client, RequestBuilder, ResponseBuilder
from ..models import SystemVersion


@dataclass(frozen=True)
class SystemVersionCommand:
    client: Client

    def execute(self) -> SystemVersion:
        return self.client.execute(
            RequestBuilder({request.method!r}, {request.path!r}),
            ResponseBuilder(SystemVersion.from_wire),
        )
''',
        "commands/__init__.py": generated + '''from .system_version import SystemVersionCommand

__all__ = ["SystemVersionCommand"]
''',
        "client.py": generated + f'''from docker_python.core import Client, Transport
from .commands import SystemVersionCommand


class DockerClient(Client):
    def __init__(self, transport: Transport):
        super().__init__(transport, {version!r})

    def system_version(self) -> SystemVersionCommand:
        return SystemVersionCommand(self)
''',
        "__init__.py": generated + '''from .client import DockerClient

__all__ = ["DockerClient"]
''',
    }
    list_files, commands = generate_list_commands(spec)
    files.update(list_files)
    files['client.py'] = files['client.py'].replace(
        'from .commands import SystemVersionCommand',
        'from .commands import SystemVersionCommand, ' + ', '.join(name for _, name, _ in commands),
    )
    for command_module, command_name, method in commands:
        files['commands/__init__.py'] += f'\nfrom .{command_module} import {command_name}\n__all__.append({command_name!r})\n'
        files['client.py'] += f'\n    def {method}(self) -> {command_name}:\n        return {command_name}(self)\n'
    ModelGenerator(SchemaDiscovery(spec).collect()).generate(module / "models")
    for relative_path, source in files.items():
        path = module / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)


if __name__ == "__main__":
    main()
