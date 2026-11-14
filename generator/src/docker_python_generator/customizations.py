"""Select handwritten model implementations before expanding Swagger compositions."""

import tomllib
from copy import deepcopy
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Protocol

from .swagger import PYTHON_MIXIN, PYTHON_MODULE, PYTHON_NAME, PYTHON_TYPE, Schema, Swagger


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


def find_field(schema: Schema, name: str, context: SchemaContext, seen: frozenset[int] = frozenset()) -> Schema:
    schema = context.resolve(schema)
    if id(schema) in seen:
        raise ValueError(f"Cyclic inheritance at {context.location}")
    seen = seen | {id(schema)}
    matches = []
    if name in schema.get("properties", {}):
        matches.append(schema["properties"][name])
    for part in schema.get("allOf", []):
        try:
            matches.append(find_field(part, name, context, seen))
        except KeyError:
            pass
    if not matches:
        raise KeyError(name)
    if len(matches) != 1:
        raise ValueError(f"Ambiguous inherited field at {context.location}")
    return matches[0]


def apply_customizations(spec: Swagger, config: Path | None = None) -> CustomizedSpec:
    config = config or Path(__file__).with_name("customizations.toml")
    settings = tomllib.loads(config.read_text())
    result: Swagger = deepcopy(spec)
    modules: dict[str, RuntimeModule] = {}
    for section in ("fields", "definitions"):
        for target, entry in settings.get(section, {}).items():
            definition, _, field = target.partition(".")
            location = f"#/definitions/{definition}" + (f"/properties/{field}" if section == "fields" else "")
            context = SchemaContext(spec["info"]["version"], location, spec)
            output_context = SchemaContext(context.api_version, location, result)
            try:
                schema = spec["definitions"][definition]
                customized = result["definitions"][definition]
                if section == "fields":
                    schema = find_field(schema, field, context)
                    customized = find_field(customized, field, output_context)
                if entry.get("items"):
                    schema = context.resolve(schema)["items"]
                    customized = output_context.resolve(customized)["items"]
                    context = SchemaContext(context.api_version, location + "/items", spec)
            except KeyError as error:
                raise ValueError(f"API {context.api_version}: customization target missing: {location}") from error
            if "source" not in entry:
                if section != "definitions" or entry.get("mixin"):
                    raise ValueError(f"{target}: only definition renames may omit source")
                customized[PYTHON_NAME] = entry["type"]
                continue
            sources = entry["source"]
            if isinstance(sources, str):
                sources = [sources]
            matches = []
            for source in sources:
                module, _, name = source.rpartition(".")
                candidate: Customization = getattr(import_module(module), name)()
                if candidate.is_compatible_with_schema(schema, context):
                    matches.append((source, candidate))
            if len(matches) != 1:
                raise ValueError(
                    f"API {context.api_version}: {context.location}: expected exactly one compatible customization; "
                    f"found {len(matches)}; candidates={sources}; matches={[source for source, _ in matches]}"
                )
            selected = matches[0][1].runtime_modules()
            export = entry.get("mixin", entry["type"])
            owners = [module for module in selected if export in module.exports]
            if len(owners) != 1:
                raise ValueError(f"{target}: customization must export {export} exactly once")
            for module in selected:
                if not module.name.isidentifier() or any(not name.isidentifier() for name in module.exports):
                    raise ValueError(f"Invalid customization module or export: {module}")
                if module.name in modules and modules[module.name] != module:
                    raise ValueError(f"Conflicting customization modules: {module.name}")
                modules[module.name] = module
            if entry.get("mixin"):
                if section != "definitions":
                    raise ValueError("Mixins require a definition target")
                customized[PYTHON_NAME] = entry["type"]
                customized[PYTHON_MIXIN] = entry["mixin"]
            else:
                customized[PYTHON_TYPE] = entry["type"]
            customized[PYTHON_MODULE] = owners[0].name
    return CustomizedSpec(result, tuple(modules.values()))
