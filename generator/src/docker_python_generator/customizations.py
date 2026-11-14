"""Select handwritten model implementations before expanding Swagger compositions."""

import tomllib
from copy import deepcopy
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Protocol

from .swagger import PYTHON_MODULE, PYTHON_TYPE, Schema, Swagger


@dataclass(frozen=True)
class SchemaContext:
    api_version: str
    location: str
    spec: Swagger

    def resolve(self, schema: Schema) -> Schema:
        from .discovery import _do_resolve

        return _do_resolve(schema, self.spec)


@dataclass(frozen=True)
class RuntimeModule:
    name: str
    source: Path
    exports: tuple[str, ...]


class Customization(Protocol):
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool: ...

    def runtime_modules(self) -> tuple[RuntimeModule, ...]: ...


@dataclass(frozen=True)
class CustomizedSpec:
    spec: Swagger
    runtime_modules: tuple[RuntimeModule, ...]


def apply_customizations(spec: Swagger, config: Path | None = None) -> CustomizedSpec:
    config = config or Path(__file__).with_name("customizations.toml")
    settings = tomllib.loads(config.read_text())
    result: Swagger = deepcopy(spec)
    modules: dict[str, RuntimeModule] = {}
    for target, entry in settings.get("fields", {}).items():
        definition, field = target.split(".", 1)
        location = f"#/definitions/{definition}/properties/{field}"
        context = SchemaContext(spec["info"]["version"], location, spec)
        try:
            schema = spec["definitions"][definition]["properties"][field]
        except KeyError as error:
            raise ValueError(f"API {context.api_version}: customization target missing: {location}") from error
        sources = entry["source"]
        if isinstance(sources, str):
            sources = [sources]
        matches: list[tuple[str | Any, Customization]] = []
        for source in sources:
            module, _, name = source.rpartition(".")
            candidate: Customization = getattr(import_module(module), name)()
            if candidate.is_compatible_with_schema(schema, context):
                matches.append((source, candidate))
        if len(matches) != 1:
            raise ValueError(
                f"API {context.api_version}: {location}: expected exactly one compatible customization; "
                f"found {len(matches)}; candidates={sources}; matches={[source for source, _ in matches]}"
            )
        one_match = matches[0]
        one_source, one_candidate = one_match
        selected = one_candidate.runtime_modules()
        owners = [module for module in selected if entry["type"] in module.exports]
        if len(owners) != 1:
            raise ValueError(f"{target}: customization must export {entry['type']} exactly once")
        one_owner = owners[0]
        for module in selected:
            if not module.name.isidentifier() or any(not name.isidentifier() for name in module.exports):
                raise ValueError(f"Invalid customization module or export: {module}")
            if module.name in modules and modules[module.name] != module:
                raise ValueError(f"Conflicting customization modules: {module.name}")
            modules[module.name] = module
        customized = result["definitions"][definition]["properties"][field]
        customized[PYTHON_TYPE] = entry["type"]
        customized[PYTHON_MODULE] = one_owner.name
    return CustomizedSpec(result, tuple(modules.values()))
