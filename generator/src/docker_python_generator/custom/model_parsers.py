"""Compatibility checks for model parser implementations and wire wrappers."""

from dataclasses import dataclass
from pathlib import Path

from ..customizations import RuntimeModule, SchemaContext
from ..swagger import Schema

RUNTIME = Path(__file__).with_name("runtime")
MOUNT_EXPORTS = (
    "AccessMode",
    "SELContext",
    "PropagationMode",
    "Volume",
    "Volumes",
    "Bind",
    "Binds",
    "VolumesFrom",
    "Link",
    "Links",
)
PARSER_EXPORTS = ("BindingParsingMixin", "DeviceParsingMixin", "RestartPolicyParsingMixin")


def modules(*names):
    artifacts = {
        "mount_specs": RuntimeModule("mount_specs", RUNTIME / "mount_specs.py", MOUNT_EXPORTS),
        "parsing_mixins": RuntimeModule("parsing_mixins", RUNTIME / "parsing_mixins.py", PARSER_EXPORTS),
        "exposed_ports": RuntimeModule(
            "exposed_ports", RUNTIME / "exposed_ports.py", ("InternetProtocol", "ExposedPort", "ExposedPorts")
        ),
        "ports": RuntimeModule("ports", RUNTIME / "ports.py", ("PortBinding", "Ports")),
    }
    return tuple(artifacts[name] for name in names)


def contract(schema, context):
    schema = context.resolve(schema)
    ignored = {"description", "example", "default", "title", "x-nullable", "x-go-type"}
    result = {}
    for key, value in schema.items():
        if key in ignored:
            continue
        if key == "properties":
            value = {name: contract(prop, context) for name, prop in value.items()}
        elif key in ("items", "additionalProperties") and isinstance(value, dict):
            value = contract(value, context)
        result[key] = value
    return result


@dataclass(frozen=True)
class ExposedPortsCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        schema = context.resolve(schema)
        values = schema.get("additionalProperties")
        if not isinstance(values, dict):
            return False
        values = context.resolve(values)
        # Ignore documentation; reject unfamiliar structural constraints.
        documentation = {"description", "example", "title", "default"}
        return (
            schema.get("type") == "object"
            and not (schema.keys() - documentation - {"type", "additionalProperties", "x-nullable"})
            and values.get("type") == "object"
            and values.get("enum") == [{}]
            and not (values.keys() - documentation - {"type", "enum"})
        )

    def runtime_modules(self) -> tuple[RuntimeModule, ...]:
        return modules("exposed_ports")


@dataclass(frozen=True)
class VolumesCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        return contract(schema, context) == {"type": "object", "additionalProperties": {"type": "object", "enum": [{}]}}

    def runtime_modules(self):
        return modules("mount_specs")


@dataclass(frozen=True)
class StringListCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        return contract(schema, context) == {"type": "array", "items": {"type": "string"}}

    def runtime_modules(self):
        return modules("mount_specs")


@dataclass(frozen=True)
class StringCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        return contract(schema, context) == {"type": "string"}

    def runtime_modules(self):
        return modules("mount_specs")


@dataclass(frozen=True)
class BindingCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        return contract(schema, context) == {
            "type": "object",
            "properties": {"HostIp": {"type": "string"}, "HostPort": {"type": "string"}},
        }

    def runtime_modules(self):
        return modules("parsing_mixins")


@dataclass(frozen=True)
class DeviceCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        return contract(schema, context) == {
            "type": "object",
            "properties": {
                "PathOnHost": {"type": "string"},
                "PathInContainer": {"type": "string"},
                "CgroupPermissions": {"type": "string"},
            },
        }

    def runtime_modules(self):
        return modules("parsing_mixins")


@dataclass(frozen=True)
class RestartPolicyCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        shape = contract(schema, context)
        properties = shape.get("properties", {})
        names = properties.get("Name", {})
        return (
            shape.keys() == {"type", "properties"}
            and shape["type"] == "object"
            and properties.keys() == {"Name", "MaximumRetryCount"}
            and names == {"type": "string", "enum": ["", "no", "always", "unless-stopped", "on-failure"]}
            and properties["MaximumRetryCount"].get("type") == "integer"
            and not (properties["MaximumRetryCount"].keys() - {"type", "format"})
        )

    def runtime_modules(self):
        return modules("parsing_mixins")


@dataclass(frozen=True)
class PortsCustomization:
    def is_compatible_with_schema(self, schema: Schema, context: SchemaContext) -> bool:
        expected = {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"HostIp": {"type": "string"}, "HostPort": {"type": "string"}},
                },
            },
        }
        return contract(schema, context) == expected

    def runtime_modules(self):
        return modules("exposed_ports", "parsing_mixins", "ports")
