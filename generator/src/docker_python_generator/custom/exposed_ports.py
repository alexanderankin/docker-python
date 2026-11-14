from dataclasses import dataclass
from pathlib import Path

from ..customizations import Customization, RuntimeModule, SchemaContext
from ..swagger import Schema


@dataclass(frozen=True)
class ExposedPortsCustomization(Customization):
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
        return (
            RuntimeModule(
                "exposed_ports",
                Path(__file__).with_name("runtime") / "exposed_ports.py",
                ("ExposedPort", "ExposedPorts"),
            ),
        )
