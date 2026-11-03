"""Generate all models and operations from a Docker Engine Swagger document."""
import argparse
from pathlib import Path

from .commands import CommandGenerator
from .discovery import SchemaDiscovery
from .models import ModelGenerator
from .swagger import load_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('spec', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    spec = load_spec(args.spec)
    version = spec['info']['version']
    module = args.output / 'src' / 'docker_python' / 'versions' / ('v_' + version.replace('.', '_'))
    ModelGenerator(SchemaDiscovery(spec).collect()).generate(module / 'models')
    CommandGenerator(spec).generate(module)


if __name__ == '__main__':
    main()
