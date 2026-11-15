"""Generate all models and operations from a Docker Engine Swagger document."""

import argparse
from pathlib import Path

from .commands import CommandGenerator
from .customizations import apply_customizations
from .discovery import SchemaDiscovery
from .models import ModelGenerator
from .swagger import load_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--customizations", type=Path, required=False)
    args = parser.parse_args()
    spec = load_spec(args.spec)
    customization = apply_customizations(spec, args.customizations)
    spec = customization.spec
    version = spec["info"]["version"]
    module = args.output / "src" / "docker_python" / "versions" / ("v_" + version.replace(".", "_"))
    ModelGenerator(SchemaDiscovery(spec).collect(), customization.runtime_modules).generate(module / "models")
    CommandGenerator(spec).generate(module)
    (module / "py.typed").touch(exist_ok=True)
    (module / "models" / "py.typed").touch(exist_ok=True)
    (module / "commands" / "py.typed").touch(exist_ok=True)


if __name__ == "__main__":
    main()
